import Request from "@/entity/Request";
import RequestController from "@/controller/RequestController";
import Project from "@/entity/Project";

export default class ProjectController extends RequestController {
    public async create(project: Record<string, unknown>): Promise<any> {
        const request = new Request(this.apiUrl??'', this.apiToken);
        const response = await request.post('/project', project);
        return response.data;
    }

    public async listProjects(amount: number): Promise<Project[]> {
        const request = new Request(this.apiUrl??'', this.apiToken);
        const response = await request.get(`/list/projects?q=LIMIT ${amount} SORT (id, DESC)`);
        return response.data['items'].map((item: {id: number, name: string}) => {
            return new Project().setId(item.id).setName(item.name).build();
        });
    }
}