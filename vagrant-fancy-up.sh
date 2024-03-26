{
    mkdir -p ./.ssh
    vagrant up | tee >(grep -E "SSH (address|username)" | awk '/address/ {gsub(/:.*/, "", $NF); print "address: " $NF} /username/ {print "username: " $NF}' > ./.ssh/details.yaml)
    vagrant ssh-config | grep IdentityFile | awk '{print "private_key: " $2}' >> ./.ssh/details.yaml
}
