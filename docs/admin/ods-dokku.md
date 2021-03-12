# Push to the existing dokku app

These instructions are for people with deploy access to Open Data Services's servers.

These instructions are for deploying to the **live instance**.

## Add your ssh key to dokku if you haven't already

`scp` the key to the server, and then on the server:

```
dokku ssh-keys:add name_for_your_key_here path/to/your_key.pub 
```

## Set up your local git repo

On your local machine, inside a clone of this repository:

```
# Add the dokku remote
git remote add dokku-live dokku@dokku1.dokku.opendataservices.uk0.bigv.io:standards-lab-live
```

## Do a deploy

On your local machine: 

```
git push dokku-live main
```
