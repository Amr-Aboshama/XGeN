import { topics } from './../topics';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Qcount } from './../Qcount';
import { timeout} from 'rxjs/operators';


@Injectable({
  providedIn: 'root'
})
export class TopicsService {
  baseURL: string = "http://localhost:3000/";
  serverURL: string="http://localhost:5000/";
  ngRokURL: string ="http://da2e29ba31ac.ngrok.io/";

  constructor(private http: HttpClient) { }


SubmitSpecs(uuid: string , topics: string[], Qcount: Qcount): Observable<any> {

      const formdata = new FormData();
      // for(let i = 0; i < Ids.length; i++) {
      //   formData.append("Ids", Ids[i]);
      formdata.append('uuid',uuid);
      for (let i=0 ; i < topics.length ; i++){
        formdata.append('topics',topics[i]);
      }
      formdata.append('whq_count',JSON.stringify(Qcount.WH)); //for now
      formdata.append('boolq_count', JSON.stringify(Qcount.Booln) ); //for now
      formdata.append('tfq_count', JSON.stringify(Qcount.TF));
      formdata.append('mcq_count',JSON.stringify(Qcount.MCQ))
      console.log('The body in service ',formdata)

      return this.http.post(this.ngRokURL + 'api/examSpecifications',formdata );
    }

  //just for testing

  //only for test
getExam():Observable<any>{
  const headers = { 'content-type': 'application/json'}

  return this.http.get<any>(this.baseURL+'exam',{'headers':headers}).pipe(
    timeout(2147483647)
);
}

}
