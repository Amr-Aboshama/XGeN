import { topics } from './../topics';
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';


@Injectable({
  providedIn: 'root'
})
export class HomeService {
public SharedTopics: string[];
public uuid: string;

  baseURL: string = "http://localhost:3000/";
  serverURL: string="http://localhost:5000/";
  ngRokURL: string ="http://a695583c09a4.ngrok.io/"

  constructor(private http: HttpClient) { }

  //send text
  //get topics & uuid
  sendText(text : any): Observable<any> {

    const formdata = new FormData();
    formdata.append('text', text.Text);
    console.log('The body in service ',formdata)

    return this.http.post(this.ngRokURL + 'api/upload/text',formdata )
  }


postFile(fileToUpload: File): Observable<any> {
  const endpoint = this.ngRokURL+'api/upload/pdf';
  const formData: FormData = new FormData();
  formData.append('file', fileToUpload, fileToUpload.name);
  console.log("###########")
  return this.http.post(endpoint, formData)
    //.pipe(map(() => { return true; }));

}
//only for test
// getTopics():Observable<any>{
//   const headers = { 'content-type': 'application/json'}

//   return this.http.get<any>(this.baseURL+'Topics',{'headers':headers})
// }

}
