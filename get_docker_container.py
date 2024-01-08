def get_docker_container(container_name, project_name=None, try_all=False):
    import docker
    qualified_name = f'{project_name}-{container_name}' if project_name else container_name

    try:
        return client.containers.get(qualified_name)
    except (NotFound, APIError):
        if try_all:
            return client.containers.list(all=True, filters={'name': container_name})
        else:
            raise NotFound(f'No such container: {container_name}')
