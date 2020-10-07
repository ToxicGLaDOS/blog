Title: Adding a new node to the cluster
Date: 10-06-2020 20:00
Category: Pi Cluster

This is a guide on adding a new raspberry pi node to your k3s managed kubernetes cluster.


## tl;dr

1. Write Raspberry Pi OS to an sd card. [Found here](https://downloads.raspberrypi.org/raspios_lite_armhf_latest)
2. Boot er up
3. ssh in and configure
4. Install k3s


## Slightly more detailed version
1. Write Raspberry Pi OS to an sd card
    1. Download Raspberry Pi OS [Found here](https://downloads.raspberrypi.org/raspios_lite_armhf_latest)
    2. Unzip it: `unzip 2020-08-20-raspios-buster-armhf-lite.zip`
    3. Copy image to SD card: `sudo dd if=/path/to/raspberryPiOS.img of=/dev/sdX bs=4M conv=fsync` (where /dev/sdX is the SD card device)
    4. Mount SD card: `sudo mount /dev/sdX /mnt/sdcard` (`/mnt/sdcard` can be any empty directory)
    5. Add "ssh" file to filesystem which causes the ssh server to start on boot: `sudo touch /mnt/sdcard/ssh`
    6. Unmount it: `sudo umount /mnt/sdcard`
2. Boot 'er up
    1. Put the SD card in the pi
    2. Plug in the pi
    3. Give it a minute or two
3. ssh in and configure
    1. ssh in: `ssh pi@raspberrypi` password is "raspberry"
    2. Update and install vim and curl: `sudo apt update && sudo apt upgrade -y && sudo apt install -y vim curl` Although `vim` isn't strictly necessary and `curl` is on the image by default, I like vim and we'll use curl later so better to make sure it's already there.
    3. Make yourself a user: `sudo useradd -m -G adm,dialout,cdrom,sudo,audio,video,plugdev,games,users,input,netdev,gpio,i2c,spi jeff`
        1. `adm,dialout,cdrom,sudo,audio,video,plugdev,games,users,input,netdev,gpio,i2c,spi` are groups that you are adding your user to. The only _super_ important one is probably `sudo`. This is the list that the default `pi` user starts in so might as well.
    4. Create a `.ssh` directory so you can get in to your user: `sudo -u jeff mkdir .ssh`
        1. We use `sudo -u jeff` here so that it runs as the jeff user and makes `jeff` the owner by default
    5. Slap your public ssh keys into the authorized_keys file: `sudo -u jeff curl https://github.com/ToxicGLaDOS.keys -o /home/jeff/.ssh/authorized_keys` Here we curl the key down from a github account straight into the authorized_keys file. If your keys aren't on github you might `scp` them onto the pi.
    6. Change the hostname of your machine by editing the `/etc/hosts` and `/etc/hostname` files. This can be done manually or with some handy `sed` commands.
        1. `sudo sed -i s/raspberrypi/myHostname/g /etc/hosts`
        2. `sudo sed -i s/raspberrypi/myHostname/g /etc/hostname`
    7. Disable password authentication into the pi (optional, but pretty nice)
        1. Manually: Open `/etc/ssh/sshd_config` and edit the line that says `#PasswordAuthentication yes` so it says `PasswordAuthentication no`. If this line doesn't exist add the `PasswordAuthentication no` line.
        2. Automatic (relies on commented version being there): `sudo sed -i s/#PasswordAuthentication\ yes/PasswordAuthentication\ no/g /etc/ssh/sshd_config`
    8. Allow passwordless `sudo`: `echo 'jeff    ALL=(ALL) NOPASSWD:ALL' | sudo tee -a /etc/sudoers` This is a little dangerous, because if your account on the machine gets comprimised then an attacker could run any program as root :(. Also if you fail to give yourself passwordless `sudo` access and restart the pi you can end up being unable to `sudo` at all which means you can't access `/etc/sudoers` to give yourself `sudo` access... So you might end up having to re-imaging the SD card cause you're boned. Not that that has happened to me of course... :(
    9. Delete the default pi user: `sudo userdel -r pi`
4. Install k3s
    1. `curl -sfL https://get.k3s.io | K3S_URL=https://masterNodeHostname:6443 K3S_TOKEN=yourToken sh -` This pulls down a script provided by k3s and runs it so maybe check to make sure k3s is still up and reputable. Make sure to replace masterNodeHostname and yourToken with your values. masterNodeHostname is the hostname of the master node in your cluster (probably the first one you set up), in my case it's `raspberry0`. yourToken is an access token used to authenticate to your master node. It can be found on your master node in the `/var/lib/rancher/k3s/server/node-token` file. Read more at [k3s.io](https://k3s.io/).


That's basically it!

