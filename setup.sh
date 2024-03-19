#!/usr/bin/env bash

########################################
#
# Setting up the new image to run
# this service (aws)
#
#  Ubuntu
#
#  wget https://raw.githubusercontent.com/forestbiotech-lab/ontoBrAPI/master/setup.sh 
#
########################################


echo -n USERNAME: 
read USERNAME

sudo adduser ${USERNAME}
sudo usermod -aG sudo,adm,sudo ${USERNAME}

sudo mkdir /home/${USERNAME}/.ssh
sudo cp /home/ubuntu/.ssh/authorized_keys /home/${USERNAME}/.ssh/authorized_keys
sudo chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.ssh/authorized_keys
sudo chmod 644 /home/${USERNAME}/.ssh/authorized_keys


#Docker 
sudo apt update 
sudo apt install -y build-essential 
# Add Docker's official GPG key:
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sleep 10;
sudo usermod -aG docker ${USERNAME}
sudo systemctl start docker
#docker-compose
sudo curl -SL https://github.com/docker/compose/releases/download/v2.24.6/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

#Login to USERNAME and finish install

sudo wget https://raw.githubusercontent.com/forestbiotech-lab/ontoBrAPI/master/reposetup.sh -O /home/${USERNAME}/reposetup.sh
sudo chown ${USERNAME}:${USERNAME} /home/${USERNAME}/reposetup.sh
sudo chmod 777 /home/${USERNAME}/reposetup.sh
sudo --user ${USERNAME} /home/${USERNAME}/./reposetup.sh
echo -e "Finished install, for ${USERNAME}, repos are located in the ~/git folder."
echo "Now open up http://$(dig +short myip.opendns.com @resolver1.opendns.com) in your browser to test this project"
sudo sh -c "cd /home/${USERNAME}; sudo su ${USERNAME}"








