#!/bin/bash
# run only as root

useradd -m -s /bin/bash deploy

mkdir -p /usr/local/bin/deploy

#need to copy sudoers file and make absolutely sure it is 440, otherwise sudo does not run
chmod 440 deploy
cp deploy /etc/sudoers.d/
chmod 440 /etc/sudoers.d/deploy
chown root: /etc/sudoers.d/deploy

#create tmp folder for temporary deploy archives, allow everybody from the group to use it
mkdir -p /home/deploy/tmp
#chmod -R g+w /home/deploy #this line removes an ability to login for user 'deploy' without password
chmod g+rwx /home/deploy/tmp

#allow mercurial user to ssh for deploy user without password
mkdir -p /home/deploy/.ssh
cat mercurial_ssh_key_pub >> /home/deploy/.ssh/authorized_keys
#.ssh folder rights should be proper
#http://unix.stackexchange.com/questions/36540/why-am-i-still-getting-a-password-prompt-with-ssh-with-public-key-authentication
chmod 600 /home/deploy/.ssh/authorized_keys
chmod 700 /home/deploy/.ssh

#change owner for all created files
chown -R deploy: /home/deploy
