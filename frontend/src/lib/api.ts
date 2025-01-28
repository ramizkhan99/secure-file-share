import axios, { AxiosRequestConfig, AxiosResponse } from "axios";

export class Api {
  private static apiUrl = import.meta.env.VITE_API_URL as string;

  public static async delete(path: string, config?: AxiosRequestConfig) {
    const response = await axios.delete(`${Api.apiUrl}/${path}`, config);
    return response;
  }

  public static async get(
    path: string,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse> {
    const response = await axios.get(`${Api.apiUrl}/${path}`, config);
    return response;
  }

  public static async post(
    path: string,
    data: unknown,
    config?: AxiosRequestConfig
  ) {
    const response = await axios.post(`${Api.apiUrl}/${path}/`, data, config);
    return response;
  }
}
