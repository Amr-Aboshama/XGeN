import { topics } from './../topics';
import { HomeService } from './home.service';
import { Component, OnInit } from '@angular/core';
import { FormGroup,FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';



@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
// public TextForm: FormGroup;
baseURL: string = "http://localhost:3000/";
serverURL: string = "http://localhost:5000/api/upload/pdf";


public TextForm: FormGroup ;
public Topics: topics[];

fileToUpload: File | null = null;

showSpinner: boolean;
isLoadingText: boolean;
isLoadingPDF : boolean;
Allow: boolean; // enable pdf button
// uploader: FileUploader = new FileUploader(
//   { url: this.serverURL, removeAfterUpload: false, autoUpload: true });
  constructor(private fb: FormBuilder,private route: ActivatedRoute,private HttpService: HomeService, private router: Router) {
    this.createText();
    this.isLoadingText=false;
    this.isLoadingPDF= false;
    this.Allow = false;
    localStorage.clear(); //clear before every run



   }

  ngOnInit(): void {
  }


createText(){
this.TextForm = this.fb.group({
  Text:['', Validators.required]
})
}

SendText() {
  this.isLoadingText=true;
  this.HttpService.sendText(this.TextForm.getRawValue())
    .subscribe(data => {
      data => {
        if (data) {
          //this.hideloader();
          this.isLoadingText=false;
      }


       (err: any) => console.log(err);

      }
      this.HttpService.SharedTopics = data.topics,
       this.HttpService.uuid = data.uuid,
       localStorage.setItem("uuid", this.HttpService.uuid ),
       localStorage.setItem('topics', JSON.stringify(this.HttpService.SharedTopics)),
      console.log("i am the http service shaaaaaaared topics", this.HttpService.SharedTopics ),
      console.log("i am the  uuid ->>>>>>>", this.HttpService.uuid  )
      this.router.navigate(['/topics'])
    } )
}

handleFileInput(event: Event) {

console.log("eveeent");
  this.fileToUpload = (event.target as HTMLInputElement).files[0];
  console.log("fiiiiile");
  if(this.fileToUpload){
    this.Allow = true;
  }
}
uploadFileToActivity() {
  this.isLoadingPDF=true;
  this.HttpService.postFile(this.fileToUpload).subscribe(data => {
    if (data) { this.isLoadingPDF=false;}

    // do something, if upload success
    this.HttpService.SharedTopics = data.topics,
       this.HttpService.uuid = data.uuid,
       localStorage.setItem("uuid", this.HttpService.uuid ),
       localStorage.setItem('topics', JSON.stringify(this.HttpService.SharedTopics)),
      console.log("i am the http service shaaaaaaared topics", this.HttpService.SharedTopics ),
      console.log("i am the  uuid ->>>>>>>", this.HttpService.uuid  )
    console.log("i am the pDF DATAAA",data)
    this.router.navigate(['/topics'])

    }, error => {
      console.log(error);
      this.isLoadingPDF= false;
    });
}

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

hideloader() {

  // Setting display of spinner
  // element to none
  document.getElementById('loading')
      .style.display = 'none';
}

}
