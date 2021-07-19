import { topics } from './../topics';
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { timeout} from 'rxjs/operators';


@Injectable({
  providedIn: 'root'
})
export class HomeService {
//public SharedTopics: string[];
//public uuid: string;


  baseURL: string = "http://localhost:3000/";
  serverURL: string="http://localhost:5000/";
  ngRokURL: string ="http://9fce0df5024a.ngrok.io/"

  constructor(private http: HttpClient) { }

  //send text
  //get topics & uuid
  sendText(text : any): Observable<any> {

    const formdata = new FormData();
    formdata.append('text', text.Text);
    console.log('The body in service ',formdata)

    return this.http.post(this.ngRokURL + 'api/upload/text',formdata )
  }


postFile(fileToUpload: File , pdf : any): Observable<any> {
  const endpoint = this.ngRokURL+'api/upload/pdf';
  const formData: FormData = new FormData();
  formData.append('file', fileToUpload, fileToUpload.name);
  if(pdf.start == '')
  formData.append('start','1');
  else
  formData.append('start', pdf.start);
  if(pdf.end == '')
  formData.append('end','-1');
  else
  formData.append('end',pdf.end);

  console.log("###########")
  return this.http.post(endpoint, formData);


}

heartBeat(uuid : string , filename : string) : Observable<any>{
  console.log('heartbeat');
  const formdata = new FormData();
  formdata.append('uuid', uuid);
  formdata.append('filename' , filename);

  return this.http.post(this.ngRokURL+'api/heartbeat',formdata);
}
//only for test
// getTopics():Observable<any>{
//   const headers = { 'content-type': 'application/json'}

//   return this.http.get<any>(this.baseURL+'Topics',{'headers':headers})
// }


}
