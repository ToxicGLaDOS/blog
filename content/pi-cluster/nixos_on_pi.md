Title: Building cross architecture nixos images
Date: 06-15-2026 23:52 -0500
Category: Pi Cluster

## The motivation

So you have a raspberry pi and want to run nixos, but no mini HDMI to HDMI converter?
Or perhaps you just want to configure your raspberry pi remotely with nix.
There's lots of resources, maybe you should just google it.
Oh.. Everyone uses flakes, and there's a million different ways to do it, and some seem to not be supported anymore :/
Here I aim to set up a raspberry pi on nixos with `ssh` enabled an my key on it, ready for remote configuration in a way that seems to be up to date (at least as of date of publication).

## Some terminology

`nixos-rebuild` has options with names that could be confusing, but to be consistent I'll also reference them in the text, so I'm going to define them here as I understand them:

* "local host" The host that you're running your commands from. The one who's screen you're looking at. Likely an x86_64 machine. This isn't a `nixos-rebuild` option, but is still relevant to our guide here.
* "build host" The host that builds the nix deviations. In this guide this will usually be the same as the local host. (used via --build-host in `nixos-rebuild`)
* "target host" The host that your nixos builds are being built for. In this guide this will usually be the raspberry pi. (used via --target-host in `nixos-rebuild`)

## How I did it

First off, if you're on x86_64 and trying to build for a pi on aarch64 you'll need to be able to cross compile. To do that add this to your personal `configuration.nix` on your local host.

```nix
boot.binfmt.emulatedSystems = [
  "aarch64-linux"
];
```

then run a switch to actually enable it

```sh
sudo nixos-rebuild switch
```

Now we make a file called `sd-card.nix` (the name doesn't actually matter) on our local host which will serve to create an image that we can flash to our SD card which has nixos, ssh, and our key ready to go.
`sd-card.nix` should look like this

```{ .nix filename="sd-card.nix" }
# This file creates the simplest image possible while
# adding a user with our ssh key so we can boot
# and configure the machine remotely
# You can build the image with this command:
# env NIX_PATH="nixos-config=<path/to/this/file>:nixpkgs=channel:nixos-26.05" nixos-rebuild build-image --image-variant sd-card
{ config, pkgs, ... }:

{
  # Recommended by warning message
  # What this actually does... :shrug:
  boot.zfs.forceImportRoot = false;

  # Not having this results in building an image
  # for the platform of machine which is making the sd-image
  # probably x86_64.
  # We want a raspberry pi image, so we need this
  nixpkgs = {
    hostPlatform = "aarch64-linux";
  };

  # == This is the meat of what we're trying to do here ==

  # We need this to run nixos-rebuild with the local machine as the build host
  # With this you can run
  # nixos-rebuild switch -I nixos-config=configuration.nix --target-host jeff@raspberry0
  # If you try this without being a trusted-user you'll get this error:
  # error: cannot add path '/nix/store/09w0mk3fqcwblx2px3b8qzh4r6r6cna0-users-groups.json' because it lacks a signature by a trusted key
  # Without this you can run this instead:
  # nixos-rebuild switch -I nixos-config=configuration.nix --target-host jeff@raspberry0 --build-host jeff@raspberry0
  # https://mynixos.com/nixpkgs/option/nix.settings.trusted-users
  nix.settings.trusted-users = [
    "jeff"
  ];

  # Create our user
  users.users.jeff = {
    openssh.authorizedKeys.keys = [
      # Replace this with your key
      "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICEKeehduYbblNR/+ylIh83qC0JUbawjJU6hU5kF8EGl jeff@nixos"
    ];
    isNormalUser = true;
    # Add ourselves to wheel because we give wheel
    # password-less sudo access
    extraGroups = [ "wheel" ];
  };

  # Allow our user access without a password
  security.sudo.wheelNeedsPassword = false;
  
  # Enable ssh so we can do the real configuration remotely
  services.openssh.enable = true;

  # This value determines the NixOS release from which the default
  # settings for stateful data, like file locations and database versions
  # on your system were taken. It‘s perfectly fine and recommended to leave
  # this value at the release version of the first install of this system.
  # Before changing this value read the documentation for this option
  # (e.g. man configuration.nix or on https://nixos.org/nixos/options.html).
  system.stateVersion = "26.05"; # Did you read the comment?
}
```

Now you can build the image like this:
```sh
env NIX_PATH="nixos-config=</path/to/sd-card.nix>:nixpkgs=channel:nixos-26.05" nixos-rebuild build-image --image-variant sd-card
```

The last line of the output will be something like this:
```text
Done. The disk image can be found in /nix/store/1d761gdrvc48n8rd06iy4inm0m4br4j7-nixos-image-sd-card-26.05.1550.bd0ff2d3eac2-aarch64-linux.img.zst/sd-image/nixos-image-sd-card-26.05.1550.bd0ff2d3eac2-aarch64-linux.img.zst
```

Make sure it's for the correct architecture (aarch64 in my case) by checking for it in the file name.
(`nixos-image-sd-card-26.05.1550.bd0ff2d3eac2-aarch64-linux.img.zst` has `aarch64` in it.)

A symlink named `result` will have been created which points to the directory containing `sd-image`,
so you can get to the file at `./result/sd-image/<file name>`.
Note that it's compressed though, so we'll have to decompress it before putting it on the sd card.
You can do that like this

```sh
# Install zstd to decompress
nix-shell -p zstd
# Do the decompression
unzstd ./result/sd-image/nixos-image-sd-card-26.05.1550.bd0ff2d3eac2-aarch64-linux.img.zst --output-dir-flat .
# Copy the decompressed image onto the SD card.
# Make sure that of=/dev/sdX is replaced with the correct device for your SD card!
sudo dd if=nixos-image-sd-card-26.05.1550.bd0ff2d3eac2-aarch64-linux.img of=/dev/sdX bs=4096 conv=fsync status=progress
```

Now pop that SD card into your raspberry-pi.
You should be able to `ssh` into it with your key that was already configured.
We need to get the `hardware-configuration.nix` from the pi.
To do that run these commands:

```sh
# Failing to do this mount will result in a config
# which doesn't have the firmware mounted which...
# probably has consequences, but I haven't run into them yet :shrug:
# Either way, I'm pretty sure it's supposed to be mounted
# because it's referenced a lot here: https://www.raspberrypi.com/documentation/computers/configuration.html
sudo mkdir -p /boot/firmware
sudo mount /boot/firmware
sudo nixos-generate-config
```

Then copy `/etc/nixos/hardware-configuration.nix` from the pi to the host. Something like this:

```sh
scp <user>@<host>:/etc/nixos/hardware-configuration.nix .
```

for me the `hardware-configuration.nix` looked like this:

```{ .nix filename="hardware-configuration.nix" }
# Do not modify this file!  It was generated by ‘nixos-generate-config’
# and may be overwritten by future invocations.  Please make changes
# to /etc/nixos/configuration.nix instead.
{ config, lib, pkgs, modulesPath, ... }:

{
  imports =
    [ (modulesPath + "/installer/scan/not-detected.nix")
    ];

  boot.initrd.availableKernelModules = [ "xhci_pci" ];
  boot.initrd.kernelModules = [ ];
  boot.kernelModules = [ ];
  boot.extraModulePackages = [ ];

  fileSystems."/" =
    { device = "/dev/disk/by-uuid/44444444-4444-4444-8888-888888888888";
      fsType = "ext4";
    };

  fileSystems."/boot/firmware" =
    { device = "/dev/disk/by-uuid/2178-694E";
      fsType = "vfat";
      options = [ "fmask=0022" "dmask=0022" ];
    };

  swapDevices = [ ];

  nixpkgs.hostPlatform = lib.mkDefault "aarch64-linux";
}
```

This file was consistent across many reinstalls (I thought the uuids might be random, but no), and also the same as I've seen [out in the wild](https://discourse.nixos.org/t/nixos-raspberry-pi-4-setup/64190) (sans the `/boot/firmware` mount).
That means you can probably copy my `hardware-configuration.nix` if you're running on a pi4 (or maybe even others? :shrug:)

I couldn't figure out a way to determine what should be in `hardware-configuration.nix` without booting the machine first, unfortunately. You can't just run the `nixos-rebuild switch ...` without defining that stuff, which makes sense, so this will have to do.

Now you can make your real configuration file for the target machine. The most basic configuration may look like this:

```{ .nix filename="configuration.nix" }
# Now that we have nixos running on the pi
# we can configure it with a mostly normal configuration.nix
# The main gotchas are importing <nixos-hardware/raspberry-pi/4>
# and setting boot.kernelPackages, but otherwise, you're basically
# free to do normal stuff here.
# Push this config to the target machine by running this on your machine:
# nixos-rebuild switch -I nixos-config=<path/to/this/file> --target-host <user>@<host> --sudo
{ config, pkgs, ... }:

{

  imports = [
    <nixos-hardware/raspberry-pi/4>
    ./hardware-configuration.nix
  ];

  # Notice we don't actually need these anymore.
  # They were just for the sd-image creation, and
  # seem to have no use anymore as far as I can tell
  #
  #boot.zfs.forceImportRoot = false;
  #
  #nixpkgs = {
  #  hostPlatform = "aarch64-linux";
  #};

  boot = {
    # Not setting this value results in compiling the linux kernel
    # which takes many hours.
    kernelPackages = pkgs.linuxPackages;
  };

  # We need this to run nixos-rebuild with the local machine as the build host
  # With this you can run
  # nixos-rebuild switch -I nixos-config=configuration.nix --target-host jeff@raspberry0
  # If you try this without being a trusted-user you'll get this error:
  # error: cannot add path '/nix/store/09w0mk3fqcwblx2px3b8qzh4r6r6cna0-users-groups.json' because it lacks a signature by a trusted key
  # Without this you can run this instead:
  # nixos-rebuild switch -I nixos-config=configuration.nix --target-host jeff@raspberry0 --build-host jeff@raspberry0
  # https://mynixos.com/nixpkgs/option/nix.settings.trusted-users
  nix.settings.trusted-users = [
    "jeff"
  ];

  security.sudo.wheelNeedsPassword = false;
  users.users.jeff = {
    openssh.authorizedKeys.keys = [
      "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICEKeehduYbblNR/+ylIh83qC0JUbawjJU6hU5kF8EGl jeff@nixos"
    ];

    isNormalUser = true;
    extraGroups = [ "wheel" ];
  };

  # Install some packages so we have an easy
  # way to verify we're on the new generation
  environment.systemPackages = with pkgs; [
    neovim
  ];

  services.openssh.enable = true;

  # This value determines the NixOS release from which the default
  # settings for stateful data, like file locations and database versions
  # on your system were taken. It‘s perfectly fine and recommended to leave
  # this value at the release version of the first install of this system.
  # Before changing this value read the documentation for this option
  # (e.g. man configuration.nix or on https://nixos.org/nixos/options.html).
  system.stateVersion = "26.05"; # Did you read the comment?
}
```

Notice that it's essentially the same as `sd-card.nix`, but we removed
`boot.zfs.forceImportRoot` (unclear why the warning doesn't appear anymore)
and `nixpkgs.hostPlatform = "aarch64-linux"` (because it's included in `hardware-configuration.nix`.
We also add a neovim installation so we have an easy way to verify that we're
on the new generation after deploying it.

Before we deploy it though we need to set up the channels on our _local machine_.
You may think that the target machine's channels would be used, or maybe even the build machine's
but no, it's the _local machine_ as far as I can tell.

```sh
# You probably already have these first two
# And you may want to use a channel other than unstable
# that's up to you
sudo nix-channel --add https://nixos.org/channels/nixpkgs-unstable nixpkgs
sudo nix-channel --add https://nixos.org/channels/nixos-unstable nixos

# This one was new to me, so make sure you have it!
sudo nix-channel --add https://github.com/NixOS/nixos-hardware/archive/master.tar.gz nixos-hardware
sudo nix-channel --update
```

Now to actually deploy it! This is how you do that from your local machine:

```sh
# The --sudo flag has nixos run the command as root on the target host
# NOTE: If you don't have passwordless sudo available on the target host
# then you'll probably want to use the --ask-sudo-password flag.
nixos-rebuild switch -I nixos-config=configuration.nix --target-host <user>@<target host> --sudo
```

Make sure that `neovim` was installed by running `nvim` on the target machine.
If that works then you're ready to configure your pi the way you want!

Note: I've seen reports the [generation being reset after rebooting](https://discourse.nixos.org/t/generation-resets-on-reboot-on-raspberry-pi-5/59703/9), so I recommend checking for that by rebooting and checking for `nvim` again.

## Errors and how to fix them:

### file 'nixos-hardware/raspberry-pi/4' was note found...

```text
error: file 'nixos-hardware/raspberry-pi/4' was not found in the Nix search path (add it using $NIX_PATH or -I)
```

You need to have the `nixos-hardware` channel added to the _local machine_, not the raspberry pi.
You can do that with:

```sh
sudo nix-channel --add https://github.com/NixOS/nixos-hardware/archive/master.tar.gz nixos-hardware
sudo nix-channel --update
```

And yes, adding it to root's nix-channels (because sudo) works
despite the fact that we run `nixos-rebuild` as a non-root user i.e.:

```sh
nixos-rebuild switch -I nixos-config=configuration.nix --target-host jeff@raspberry0 --sudo
```

Maybe because we're running it with `--sudo`? But I thought that applied to the target machine :shrug:

### Cannot build [...] Reason: platform mismatch

```text
error: Cannot build '/nix/store/gp64xxij16i15m9dcbmpna6pygb8nw8q-system-path.drv'.
       Reason: platform mismatch
       Required system: 'aarch64-linux'
       Current system: 'x86_64-linux'
error: Cannot build '/nix/store/cjx88xnxjbqc95cf8554i3wbc7b1c6q8-dbus-1.drv'.
       Reason: 1 dependency failed.
       Output paths:
         /nix/store/ihbwly656sqdn49aklba5wlg5cja9lq2-dbus-1
error: Cannot build '/nix/store/h7x98bsyrrx1f5id7wqs7jg5am4i01yx-etc.drv'.
       Reason: 1 dependency failed.
       Output paths:
         /nix/store/mpml2v1alvnfw7a62qqg7vr9bl49v973-etc
error: Cannot build '/nix/store/0638xx5m803k2gv4zgkagzhqmzzh38iy-nixos-system-nixos-26.11pre1011622.a799d3e3886d.drv'.
       Reason: 1 dependency failed.
       Output paths:
         /nix/store/ib5b1av866p2ypr2g9ggx4w3idhrpshd-nixos-system-nixos-26.11pre1011622.a799d3e3886d
error: Build failed due to failed dependency
```

The key part here is `Reason: platform mismatch`.
If you're on x86_64 and trying to be the build-host for a raspberry pi, then you'll need cross compilation support.
To do that add these lines to your `configuration.nix` on your local machine (probably `/etc/nixos/configuration.nix`):

```nix
boot.binfmt.emulatedSystems = [
  "aarch64-linux"
];
```

and of course run a switch to actually enable it

```sh
sudo nixos-rebuild switch
```

### nixos evaluation warning: `system.build.image` is defined, while `system.build.images` is used.

The warning in full:

```text
evaluation warning: `system.build.image` is defined, while `system.build.images` is used.
                    The former will conflict with variants in the latter.
                    Maybe you are importing an image-building module into the toplevel?
                    Add it to `image.modules` instead, or adjust priorities manually.
```

This is just a warning and didn't seem to actually stop it from working, however the solution is simple.
If you see this then you likely have this defined in your `sd-card.nix`

```nix
imports = [
    <nixpkgs/nixos/modules/installer/sd-card/sd-image-aarch64.nix>
  ];
```

When using `nixos-rebuild build-image [...]` you don't need that. According to [this post](https://discourse.nixos.org/t/nixos-rebuild-build-image-error-option-system-build-images-no-value-defined/63671/6) you would use that import when running `nix build [...]` to build the image.
This is one of the reasons why this process is so confusing, the config you need depends on the command you intend to use to build the image. :(

#### Some resources I used as reference that might be useful to you
<https://michael.stapelberg.ch/posts/2025-06-01-nixos-installation-declarative/>

<https://nix.dev/tutorials/cross-compilation.html#specifying-the-host-platform>

<https://jcd.pub/2025/01/30/nixos-on-raspi-in-2025/>

<https://discourse.nixos.org/t/nixos-rebuild-build-image-error-option-system-build-images-no-value-defined/63671/7>

<https://nixos.wiki/wiki/Creating_a_NixOS_live_CD>
