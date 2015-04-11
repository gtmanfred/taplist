centos-1-nova:
  provider: my-nova
  size: performance1-1
  image: CentOS 7 (PVHVM)
  ssh_key_name: <key_name>
  flush_mine_on_destroy: True
  networks:
    - net-id: 11111111-1111-1111-1111-111111111111
    - net-id: 00000000-0000-0000-0000-000000000000
