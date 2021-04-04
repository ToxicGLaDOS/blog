Title: Setting up an nfs server for persistent storage in k8s
Date: 04-02-2021 12:00
Category: Pi Cluster

These are some helpful tips I found when trying to set up an nfs for persistent volumes on my k8s cluster. Setting up the actual persistent volumes and claims will come later.


## Prerequisites

Some of the specifics of these tips (package names, directories, etc.) are going to be specific to voidlinux which is the flavor of linux I'm running my nfs on. There is almost certainly an equivalent in your system, but the name may be different.

## tl;dr
* Make sure you have the `statd`, `nfs-server`, and `rpcbind` services enabled on the server.
* Use `/etc/exports` to configure what directories are exported.
* Run `exportfs -r` to make changes to `/etc/exports` real.

## Setup
Actually setting up the nfs is pretty easy.
Just install the `nfs-utils` package and enable the `nfs-server`, `statd`, and `rpcbind` services.
That's it.

## Configuration

Now that you have an nfs server you need to configure which directories are available for a client to mount.
This is done through the `/etc/exports` file.
I found [this site](https://www.thegeekdiary.com/mount-nfs-access-denied-by-server-while-mounting-how-to-resolve/) to be quite useful in explaining what some of the options in `/etc/exports` are and what they mean.
Specifically, debugging step 3 (setting the options to `(ro,no_root_squash,sync)`) was what finally got it working for me when I was receiving `mount.nfs: access denied by server while mounting 192.168.0.253:/home/jeff/test`.
My `/etc/exports` file is just one line:
```
/watermelon-pool 192.168.0.0/24(rw)
```
* `/watermelon-pool` is the path to my zfs pool which is where I store this kind of data.

* `192.169.0.0/24` is the network prefix that my machines are in.

* `(rw)` allows those machines to read and write to the nfs

After you make changes to `/etc/exports` make sure to run `exportfs -r`.
`exportfs -r` rereads the `/etc/exports` and exports the directories specified in `/etc/exports`.
Essentially, you need to run it every time you edit `/etc/exports`.

For some reason I had issues when not specifying the `no_root_squash` option for some directories.
I still don't have a good answer for what's up with that, but you can read my (still unanswered) [question on unix stack exchange](https://unix.stackexchange.com/questions/643298/mount-nfs4-access-denied-by-server-while-mounting-after-changing-different-sh) if you want.
This didn't effect my ability to use this nfs server as a place for persistent storage for kubernetes though.
It seemed to be a void specific bug that only effects certain directories (specifically my home directory), but I'm still not sure.

## Read the docs

Unsurprisingly the [voidlinux docs on setting up an nfs server on voidlinux](https://docs.voidlinux.org/config/network-filesystems.html) were pretty helpful, who knew? There are a few pretty non-obvious steps when setting up an nfs on void. Notably you have to enable the `rpcbind`, and `statd` services on the nfs server in addition to the `nfs-server` service.

## Errors I received and how I fixed them

* Command: `showmount -e 192.168.0.253`

  Received: `clnt_create: RPC: Program not registered`

  Fix: Start `statd` service on server

* Command: `showmount -e 192.168.0.253`

  Received: `clnt_create: RPC: Unable to receive`

  Fix: Start `rpcbind` service on server

* Command: `sudo mount -v -t nfs 192.168.0.253:/home/jeff/test nas/`

  Received: `mount.nfs: mount(2): Connection refused`

  Fix: Start `rpcbind` service on server

* Command: `sudo sv restart nfs-server`
  
  Received: `down: nfs-server: 1s, normally up, want up`

  Fix: Start `rpcbind` and `statd` services on server

* Command: `sudo mount -v -t nfs 192.168.0.253:/home/jeff/test nas/`

  Received: `mount.nfs: mount(2): Permission denied`

## Random tips
* Make sure the `nfs-server` service is actually up.

`sv` doesn't make this super clear in my opinion. 
For example _this_ means everything is good
    
```
> sudo sv restart nfs-server
ok: run: nfs-server: (pid 9446) 1s
```
while _this_ means everything is broken

```
> sudo sv restart nfs-server
down: nfs-server: 1s, normally up, want up
```

Not quite as different I would like :/

If you find that your `nfs-server` service isn't running it might be because you haven't enabled the `statd` and `rpcbind` services.

* You can mount directories deeper than the exported directory.

For instance, if you put `/home/user *` in `/etc/exports` you can mount `/home/user/specific/path` assuming `/home/user/specific/path` exists on ths nfs server like this:

```
sudo mount -t nfs4 192.168.0.253:/home/user/specific/path /mnt/mount_point
```
