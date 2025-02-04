import JsonMapper from "@/utils/JsonMapper";
import Request from "@/entity/Request";
import RequestController from "@/controller/RequestController";
import Project from "@/entity/Project";

class ProjectController extends RequestController {
    public async create(project: Record<string, unknown>): Promise<any> {
        const request = new Request(this.apiUrl!, this.apiToken);
        const response = await request.post('/project', project);
        return response.data;
    }

    public async listProjects(amount: number): Promise<Project[]> {
        const request = new Request(this.apiUrl!, this.apiToken);
        const response = await request.get(`/list/projects?q=LIMIT ${amount} SORT (id, DESC)`);
        return JsonMapper.transformArray(
            response.data['items'],
            Project
        );
    }
}

export default ProjectController;