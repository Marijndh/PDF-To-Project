class JsonMapper {
    static transformArray<T>(json: any[], classConstructor: { new(data: any): T }): T[] {
        return json.map((item) => new classConstructor(item));
    }

    static transformSingle<T>(json: any, classConstructor: { new(data: any): T }): T {
        if (json && typeof json === 'object') {
            return new classConstructor(json);
        } else {
            throw new Error('Invalid JSON format');
        }
    }
}
export default JsonMapper;