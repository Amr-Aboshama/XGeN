import { HomeService } from './../home/home.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { topics } from './../topics';
import { Component, Input, OnInit } from '@angular/core';
import { TopicsService } from './topics.service';
import { Router } from '@angular/router';
import { interval, Observable, of, Subscription, timer } from 'rxjs';
import { catchError, filter, switchMap } from 'rxjs/operators';



@Component({
  selector: 'app-topics',
  templateUrl: './topics.component.html',
  styleUrls: ['./topics.component.css']
})
export class TopicsComponent implements OnInit {

  items: any;
  Topics : topics[];

  UserAddedTopics: string[];


  SelectedTopics: string[];
  ResponseTopics: string[];

  QForm: FormGroup;
  UserTopics: FormGroup;

  uuid : string;
  filename : string;
  exam : any[];

  subscription: Subscription;
  minutes: number;

  isLoadingExam: boolean;
  constructor(private HttpHome: HomeService, private HttpService:TopicsService,private router: Router, private fb: FormBuilder) {
    //this.getExam();//just fro test

    this.isLoadingExam = false;
    //this.Topics = home.Topics;
    this.SelectedTopics= [];
    this.ResponseTopics= [];
    this.UserAddedTopics= [];
    this.createQForm();
    this.createUserTopics();


    this.ResponseTopics = JSON.parse(localStorage.getItem('topics'));
    this.reForm() //reform in Topics: topics[] list


    this.uuid=localStorage.getItem("uuid");
    this.filename = localStorage.getItem("filename");

    console.log("ia m uuid :" , this.uuid );
    console.log("file",this.filename);

    ////////////////////////////////////////////////
    localStorage.removeItem('exam');



  }

  ngOnInit(): void {
    this.minutes = 15 *1000;
  }

  reForm(){
    this.Topics=[];
    if(this.ResponseTopics != undefined){
    for(let i = 0 ; i < this.ResponseTopics.length ; i++){
     const temp : topics = {
       topic: this.ResponseTopics[i],
       selected: false
     }
      this.Topics.push(temp);
    }
  }

   // console.log("i am the reformed topics", this.Topics);

  }


SelorUnsel(topic,i){
  let data = this.SelectedTopics.find(ele => ele == topic.topic);
  //if found then remove
  //if not found (data == null) then add
  //console.log("i am data ",data)
  if(data == null || data == undefined){
    topic.selected=true;
    this.SelectedTopics.push(topic.topic); // add if not found
    //this.selectedIndex = i;
  }
  else
  {this.SelectedTopics.forEach((element,index)=>{
    if(element== topic.topic) this.SelectedTopics.splice(index,1);
 });
 topic.selected=false;
    // let index = this.SelectedTopics.findIndex(ele => ele === topic.topic); //remove if found
    // this.SelectedTopics.splice(index, 1);//remove element from array
  }
 // console.log(this.SelectedTopics);
}

createQForm(){
  this.QForm = this.fb.group({
    WH:['', Validators.required],
    TF:['', Validators.required],
    MCQ:['', Validators.required],
    Booln:['', Validators.required]
  })
  }

  createUserTopics(){
    this.UserTopics = this.fb.group({
      UserT: ['']
    })
  }

  AddTopic(){
    this.SelectedTopics.push(this.UserTopics.getRawValue().UserT);
    this.UserAddedTopics.push(this.UserTopics.getRawValue().UserT)
   // console.log(this.SelectedTopics);
   // console.log(this.UserAddedTopics);
  }


  delUserTopic(topic){
    this.SelectedTopics.forEach((element,index)=>{
      if(element== topic) this.SelectedTopics.splice(index,1);
   });
   this.UserAddedTopics.forEach((element,index)=>{
    if(element== topic) this.UserAddedTopics.splice(index,1);

  //  console.log(this.SelectedTopics);
   // console.log(this.UserAddedTopics);
 });
  }

  submit(element, text){
    this.isLoadingExam=true;
    element.textContent = text;
    element.disabled = true;
    this.HttpService.SubmitSpecs(this.uuid,this.SelectedTopics,this.QForm.getRawValue())
    .subscribe(data => {

      this.getHeartbeat();

    }, error => {
      //alert("Error match couldn't be done please try another input")
      console.log(error)

    }
    )
  }


getHeartbeat(){

  console.log('heart beat begun');
  this.subscription = timer(0, this.minutes)
      .pipe(
        switchMap(() => {
          return this.HttpHome.heartBeat( localStorage.getItem("uuid"),localStorage.getItem("filename"))
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
          //save data in local storage
          this.exam=data.data,
          localStorage.setItem("exam", JSON.stringify(this.exam ) ),

          //turnoff spinner
          this.isLoadingExam = false;

          //unsubscribe
          console.log('i am the data ',data);
          this.subscription.unsubscribe();

          //navugate to exam
          this.router.navigate(['/exam'])
        }
        console.log(data);
      });



}


//just for test
//   getExam(){

//   this.HttpService.getExam()
//   .subscribe(
//     data => {
//       this.exam=data,
//       localStorage.setItem("exam", JSON.stringify(this.exam ) ),


//       (err: any) => console.log(err),
//       console.log(data);


//     });
// }

// Advance(){
//   this.router.navigate(['/exam'])

// }

}
