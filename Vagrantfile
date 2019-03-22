# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"
  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :machine
    config.cache.enable :generic, { :cache_dir => "/home/vagrant/.cache/pip" }

  end
  config.vm.box_check_update = false
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "forwarded_port", guest: 5672, host: 5672
  config.vm.network "forwarded_port", guest: 15672, host: 15672

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL
    chown vagrant /etc/apt/sources.list
    chmod a+w /etc/apt/apt.conf.d
  SHELL

  # config.vm.provision "file",source:"vagrant_provisions/sources.list",destination:"/etc/apt/sources.list"
  # config.vm.provision "file",source:"vagrant_provisions/pip.conf",destination:"/home/vagrant/.pip/pip.conf"
  config.vm.provision "file",source:"vagrant_provisions/30Lang",destination:"/etc/apt/apt.conf.d/30Lang"
  config.vm.provision "shell", inline: <<-SHELL
     apt-get update
     apt-get install -y rabbitmq-server redis-server postgresql libpq-dev python3-pip python3-venv
     python3 -m pip install -U pip
     rabbitmq-plugins enable rabbitmq_management
     rabbitmqadmin declare user name=admin password=123 tags=administrator
     rabbitmqadmin declare permission user=admin vhost=/ configure=.* write=.* read=.*
     #db user admin:123
     sudo -u postgres psql -c "CREATE ROLE admin PASSWORD 'md52d7f60a0f7aed62e5268be89bee5dfbf' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN;"
     sudo -u postgres createdb artige_product_pages -O admin ||true
  SHELL
  config.vm.provision "shell",privileged:false, inline: <<-SHELL
     python3 -m pip install --user -r /vagrant/requirements/local.txt
     python3 /vagrant/manage.py migrate
  SHELL
end
