Title: Installing voidlinux on a RaspberryPi
Date: 02-10-2022 18:00
Category: Pi Cluster

To install [voidlinux](https://voidlinux.org/) on a Pi we'll have to do a `chroot` install. For official documentation on installing from `chroot` for void see [here](https://docs.voidlinux.org/installation/guides/chroot.html).

We need to install via `chroot` because the live images are [made specifically for 2GB SD cards](https://voidlinux.org/download/).

> "These images are prepared for 2GB SD cards. Alternatively, use the ROOTFS tarballs if you want to customize the partitions and filesystems."

The installation can split out into 4 rough steps

1. Partition the disk (SD card in my case) you want to install void on
2. Create the filesystems on the disk
3. Copy in the rootfs
4. Configure the rootfs to your liking

## Prerequisites

Because we're going to be creating an `aarch64` system you'll need some tool that will allow you run `aarch64` binaries from a `x86` system. To accomplish this we'll need the `binfmt-support` and `qemu-user-static` packages. To install them you can run

```bash
sudo xbps-install binfmt-support qemu-user-static
```

We'll also need to enable the `binfmt-support` service. To do this, run

```bash
sudo ln -s /etc/sv/binfmt-support /var/service/
```

Now you're one step away from being able to run `aarch64` binaries in the `chroot` on your `x86` system, but we'll get to that [later](#running-aarch64-binaries).

## Partition the disk you want to install void on

This is tricky because it can depend a little based on what you want to do. In my case I didn't allocate any swap space and kept the home directory on the root partition which keeps things pretty simple.

In this case we're going to need two partitions. One 64MiB partition that is marked with the bootable flag and has the vfat type (0b in `fdisk`). And the other that takes up the rest of the SD card with type `linux` (83 in `fdisk`).

To create these partitions with `fdisk` run `sudo fdisk /dev/sda` where `/dev/sda` is the path to your disk. The path to your disk can be found running `lsblk` before and after plugging in the disk and seeing what shows up. Once `fdisk` drops you into the `repl` you can delete the existing partitions with the `d` command.

#### Create the boot partition

Make a new partition with the `n` command, make it a primary partition with `p`, make it partition 1, and leave the first sector blank, which will keep it as the default. For the last sector put `+64M` which will give us a 64MiB partition (if you're asked to remove the signature it doesn't matter because we'll be overwriting that anyway). Use the `a` command to mark partition 1 bootable and lastly use the `t` command to make partition 1 type 0b, which is vfat.

#### Create the root partition

Now the root partition, use `n` to make a new partition, then leave everything else default. This will consume the rest of the disk for this partition. Same as before, if it asks you to remove the signature it doesn't matter because we'll be overwriting now. To set the type label use the `t` command and set it to type 83 which is the linux type.

That's all we need to do to setup the partitions. Make sure to save your changes with the `w` command!

The disk should be correctly partitioned now!

## Create the filesystems on the disk

This part is easy. Assuming the device is located at `/dev/sda`, partition 1 is the boot partition, and partition 2 is the root partition, just run these two commands.

```bash
mkfs.fat /dev/sda1 # Create boot vfat filesystem
mkfs.ext4 -O '^has_journal' /dev/sda2 # Create ext4 filesystem on the root partition (with journaling)
```

## Copy in the rootfs

For this step we'll need both partitions we set up earlier to be mounted. To mount the partitions run

```bash
MOUNT_PATH='/mnt/sdcard' # Replace with any path to an empty directory. By convention it would be in /mnt

mount /dev/sda2 $MOUNT_PATH # Mount the root partition to the mount point
mkdir -p $MOUNT_PATH/boot # Create a directory named "boot" in the root partition
mount /dev/sda1 $MOUNT_PATH/boot # Mount the boot partition to that boot directory
```

Now we just need to extract the rootfs into our mount point.


```bash
MOUNT_PATH='/mnt/sdcard' # Replace with any path to an empty directory. By convention it would be in /mnt (same mount path as above)
ROOTFS_TARBALL='/home/me/Downloads/void-rpi3-PLATFORMFS-20210930.tar.xz' # Replace with the path to the tarball you download from https://voidlinux.org/download/

# x - Tells tar to extract
# f - Tells tar to operate on the file path given after the f switch
# J - Tells tar to extract using xz, which is how the rootfs happens to be compressed
# p - Tells tar to preserve permissions from the extracted directory
# -C - Tells tar where to extract the contents to
tar xfJp $ROOTFS_TARBALL -C $MOUNT_PATH
```

That's it for this step! You might notice that we didn't explicitly copy anything into the `$MOUNT_PATH/boot` directory. The rootfs provided by void contains a `/boot` directory which will get placed into the `$MOUNT_PATH/boot` directory when we extract the tarball.

## Configure the rootfs to your liking

This step is technically optional. If we just wanted to get a system up and running, we could plug the SD card in right now and it would boot up. We wouldn't have any packages (including `base-system`, which gives us `dhcpcd`, `wpa_supplicant` and other important packages), but it _would_ boot. Additionally, the RaspberryPi's (at least mine) doesn't have a hardware clock so without an `ntp` package we won't be able to validate certs (because the time will be off) which prevents us from installing packages.

Some of the things we want to configure are most easily through a `chroot`. The problem is that the binaries in the `rootfs` we copied over are `aarch64` binaries.

<a name="running-aarch64-binaries">
### Running `aarch64` binaries in the `chroot`
</a>

Because your `x86` system cannot run `aarch64` binaries we need to emulate the `aarch64` architecture inside the `chroot`. To accomplish this we copy an `x86` binary that can do that emulation for us into the `chroot`, and then pass all `aarch64` binaries through it when we go to run them.

If you've installed the `qemu-user-static` package you should have a set of `qemu-*-static` binaries in `/bin/`. For a RaspberryPi 3, we want `qemu-aarch64-static`. Copy that into the `chroot`.

```bash
cp /bin/qemu-aarch64-static <your-chroot-path>
```

Now you're ready to run the `aarch64` binaries in your `chroot`.

### Recommended configuration

To create a usable system there's a few things we need to setup that are somewhere between recommended and mandatory; the `base-system` package, `ssh` access, `ntp`, `dhcpcd` and a non-root user.

Because running commands in the `chroot` is slightly slower due to the `aarch64` emulation we'll try to setup as much of the `rootfs` as possible without actually `chroot`ing.

First we should update all the packages that were provided in the `rootfs`.

```bash
MOUNT_PATH='/mnt/sdcard' # Replace with any path to an empty directory. By convention it would be in /mnt (same mount path as above)

# Run a sync and update with the main machine's xbps pointing at our rootfs
env XBPS_ARCH=aarch64 xbps-install -Su -r $MOUNT_PATH
```

#### The base-system package

Just install the `base-system` package from your machine with the `-r` flag pointing at the `$MOUNT_PATH`.

```bash
MOUNT_PATH='/mnt/sdcard' # Replace with any path to an empty directory. By convention it would be in /mnt (same mount path as above)

# Install base-system
env XBPS_ARCH=aarch64 xbps-install -r $MOUNT_PATH base-system
```

#### ssh access

We just need to activate the `sshd` service in the `rootfs`.

```bash
MOUNT_PATH='/mnt/sdcard' # Replace with any path to an empty directory. By convention it would be in /mnt (same mount path as above)

ln -s /etc/sv/sshd $MOUNT_PATH/etc/runit/runsvdir/default/
```

There's two thing here that look odd; 1. we're symlinking to our main machines `/etc/sv/sshd` directory and 2. we're placing the symlink in `/etc/runit/runsvdir/default/` instead of `/var/service` like is typical for activating void services.

1. When we're `chroot`'ed in, or when the system is running on the Pi `/etc/sv/sshd` will point to the Pi's `sshd` service.
2. `/var/service` doesn't exists until the system is running and it when the system is up `/var/service` will be a series of symlinks pointing to `/etc/runit/runsvdir/default/` so we can just link the `sshd` service directly to the `/etc/runit/runsvdir/default/`.

For security reasons I recommend disabling password authentication.

```bash
MOUNT_PATH='/mnt/sdcard' # Replace with any path to an empty directory. By convention it would be in /mnt (same mount path as above)

sed -ie 's/#PasswordAuthentication yes/PasswordAuthentication no/g' $MOUNT_PATH/etc/ssh/sshd_config
sed -ie 's/#KbdInteractiveAuthentication yes/KbdInteractiveAuthentication no/g' $MOUNT_PATH/etc/ssh/sshd_config
```

#### npd

We need an `ntp` package because the RaspberryPi doesn't have a hardware clock so when we boot it up the time will be January 1, 1970 which causes cert failures resulting in certificate validation failures that prevent us from installing packages and more.

```bash
MOUNT_PATH='/mnt/sdcard' # Replace with any path to an empty directory. By convention it would be in /mnt (same mount path as above)

env XBPS_ARCH=aarch64 xbps-install -r $MOUNT_PATH openntpd
ln -s /etc/sv/openntpd $MOUNT_PATH/etc/runit/runsvdir/default/
```

Same as before we just install the package with our local `xbps` package manager pointing to the `chroot` and then setup the package to run at the end of symlink chain.

#### dhcpcd

The `base-system` package should have covered the install of `dhcpcd`, so all we have to do is activate the service. Like before, we'll symlink directly to the end of the symlink chain.

```bash
MOUNT_PATH='/mnt/sdcard' # Replace with any path to an empty directory. By convention it would be in /mnt (same mount path as above)

ln -s /etc/sv/dhcpcd $MOUNT_PATH/etc/runit/runsvdir/default/
```

#### A non-root user

This probably depends on your use-case, but having everything running as root is usually bad news, so setting up a non-root user which we can `ssh` in as is probably a smart idea.

This is the first part of the configuration that is truly best done inside the `chroot`, so make sure you have the filesystem mounted and have [copied the `qemu-aarch64-static`](#running-aarch64-binaries) binary into `chroot`.

```bash
MOUNT_PATH='/mnt/sdcard' # Replace with any path to an empty directory. By convention it would be in /mnt (same mount path as above)

# After executing this command all subsequent commands will act like
# you're running on Pi instead of your main machine
chroot $MOUNT_PATH 

USERNAME='me' # Replace with your desired username

groupadd -g 1000 $USERNAME # Create our user's group

# Add our user and add it to the wheel group and our personal group
# Depending on your needs you could additionally add yourself to
# other default groups like: floppy, dialout, audio, video, cdrom, optical
useradd -g $USERNAME -G wheel $USERNAME 

# Set our password interactively
passwd $USERNAME

sed -ie 's/# %wheel ALL=(ALL) ALL/%wheel ALL=(ALL) ALL/g' $MOUNT_PATH/etc/sudoers # Allow users in the wheel group sudo access
```

At this point the root account's password is still "voidlinux". We wouldn't want our system running with the default root password, so to remove it run

```bash
MOUNT_PATH='/mnt/sdcard' # Replace with any path to an empty directory. By convention it would be in /mnt (same mount path as above)

chroot $MOUNT_PATH # Run this if you're not in the chroot

passwd --delete root
```

If you set up `ssh` access and disabled password authentication you'll want to add your `ssh` key to the `rootfs`.

```bash
MOUNT_PATH='/mnt/sdcard' # Replace with any path to an empty directory. By convention it would be in /mnt (same mount path as above)
USERNAME='me' # Replace with your desired username

mkdir $MOUNT_PATH/home/$USERNAME/.ssh
cat /home/$USERNAME/.ssh/id_rsa.pub > $MOUNT_PATH/home/$USERNAME/.ssh/authorized_keys
```

#### Clean up
According to the [void docs](https://docs.voidlinux.org/installation/guides/chroot.html) we should remove the `base-voidstrap` package and reconfigure all packages in the `chroot` to ensure everything is setup correctly.

```bash
MOUNT_PATH='/mnt/sdcard' # Replace with any path to an empty directory. By convention it would be in /mnt (same mount path as above)

chroot $MOUNT_PATH

xbps-remove -y base-voidstrap
xbps-reconfigure -fa
```

Now that we're done in the `chroot` we can delete the `qemu-aarch64-static` binary that we put in there.

```bash
MOUNT_PATH='/mnt/sdcard' # Replace with any path to an empty directory. By convention it would be in /mnt (same mount path as above)

rm $MOUNT_PATH/bin/qemu-aarch64-static
```

## That's it!

Make sure to unmount the disk before removing it from your machine because we wrote a lot of data and that data might not be synced until we unmount it.

```bash
MOUNT_PATH='/mnt/sdcard' # Replace with any path to an empty directory. By convention it would be in /mnt (same mount path as above)

umount $MOUNT_PATH/boot
umount $MOUNT_PATH
```

Lastly, with some care, a lot of these steps can be combined. To see what that might look like check out [this repo](https://github.com/ToxicGLaDOS/void-rootfs-install)

Now you should be able to put the SD card into the Pi, boot it up and have `ssh` access!
