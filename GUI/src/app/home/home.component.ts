import { topics } from './../topics';
import { HomeService } from './home.service';
import { Component, OnInit } from '@angular/core';
import { FormGroup,FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { interval, Observable, of, Subscription, timer } from 'rxjs';
import { catchError, filter, switchMap } from 'rxjs/operators';



@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
// public TextForm: FormGroup;
baseURL: string = "http://localhost:3000/";
serverURL: string = "http://localhost:5000/api/upload/pdf";
public alive: boolean;
//for heartbeat
subscription: Subscription;
minutes: number;


/////////////
public TextForm: FormGroup ;
public PDFForm : FormGroup;
public Topics: topics[];

fileToUpload: File | null = null;

isLoadingText: boolean;
isLoadingPDF : boolean;
Allow: boolean; // enable pdf button

  constructor(private fb: FormBuilder,private route: ActivatedRoute,private HttpService: HomeService, private router: Router) {
    this.createText();
    this.createPDF();
    this.isLoadingText=false;
    this.isLoadingPDF= false;
    this.Allow = false;

    localStorage.clear(); //clear before every run



   }

  ngOnInit(): void {
    //Give a heartbeat every 15 seconds
    this.minutes = 15 *1000;

  }


createText(){
this.TextForm = this.fb.group({
  Text:['', Validators.required]
})
}
createPDF(){
  this.PDFForm = this.fb.group({
   start:[''],
   end:['']
  })
}

SendText(element, text) {
  this.isLoadingText=true;
  element.textContent = text;
  element.disabled = true;
  this.HttpService.sendText(this.TextForm.getRawValue())
    .subscribe(data => {

      localStorage.setItem("uuid", data.uuid ),
      /** adjustments for heartbeats */
      localStorage.setItem("filename", data.filename);
      this.getHeartbeat();
    } )
}

handleFileInput(event: Event) {

  this.fileToUpload = (event.target as HTMLInputElement).files[0];
  if(this.fileToUpload){
    this.Allow = true;
  }
}
uploadFileToActivity(element, text) {
  this.isLoadingPDF=true;
  element.textContent = text;
    element.disabled = true;
  this.HttpService.postFile(this.fileToUpload , this.PDFForm.getRawValue()).subscribe(data => {

    localStorage.setItem("uuid", data.uuid ),
    /** adjustments for heartbeats */
    localStorage.setItem("filename", data.filename);
    this.getHeartbeat();


    }, error => {
      console.log(error);
      this.isLoadingPDF= false;
    });
}

getHeartbeat(){

  //console.log('heart beat begun');
  this.subscription = timer(0, this.minutes)
      .pipe(
        switchMap(() => {
          return this.HttpService.heartBeat( localStorage.getItem("uuid"),localStorage.getItem("filename"))
            .pipe(catchError(err => {
              // Handle errors
              console.error(err);
              return of(undefined);
            }));
        }),
        filter(data => data !== undefined)
      )
      .subscribe(data => {

        if(data.status == 'Finished')
        {
          //save topics in localstorage
          //console.log("i am data.topics", data.data.topics);
          localStorage.setItem('topics', JSON.stringify( data.data.topics));

          // turn off spinner
          this.isLoadingPDF=false;
          this.isLoadingText=false;

          //unsubscribe
          this.subscription.unsubscribe();

          //navigate to next page
          this.router.navigate(['/topics'])
        }
       // console.log(data); //for testing
      });



}
//just for testing
// getTopics(){

//   this.HttpService.getTopics()
//   .subscribe(
//     data => {
//       this.Topics=data.topics,
//       this.HttpService.SharedTopics = data.topics,
//       this.HttpService.uuid = data.uuid[0],
//       localStorage.setItem("uuid", this.HttpService.uuid ),

//       //save topics for refresh
//       localStorage.setItem('topics', JSON.stringify(this.HttpService.SharedTopics)),


//       (err: any) => console.log(err),
//       console.log(data);
//       console.log(this.Topics),
//       this.router.navigate(['/topics'])

//     });
// }



}
