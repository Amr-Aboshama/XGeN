import { HomeService } from './../home/home.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { topics } from './../topics';
import { Component, Input, OnInit } from '@angular/core';
import { TopicsService } from './topics.service';
import { Router } from '@angular/router';


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
  constructor(private HttpHome: HomeService, private HttpService:TopicsService,private router: Router, private fb: FormBuilder) {
   // this.getTopics();
    //this.Topics = home.Topics;
    this.SelectedTopics= [];
    this.ResponseTopics= [];
    this.UserAddedTopics= [];
    this.createQForm();
    this.createUserTopics();
    //console.log(this.HttpHome.SharedTopics);
    //this.ResponseTopics=this.HttpHome.SharedTopics;
    this.ResponseTopics = JSON.parse(localStorage.getItem('topics'));
    this.reForm() //reform in Topics: topics[] list

    //this.uuid = this.HttpHome.uuid;
    //localStorage.setItem("uuid", this.uuid );
    this.uuid=localStorage.getItem("uuid"); //returns "xxx"
    console.log("ia m uuid :" , this.uuid );



  }

  ngOnInit(): void {
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

    console.log("i am the reformed topics", this.Topics);

  }


SelorUnsel(topic,i){
  let data = this.SelectedTopics.find(ele => ele == topic.topic);
  //if found then remove
  //if not found (data == null) then add
  console.log("i am data ",data)
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
  console.log(this.SelectedTopics);
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
    console.log(this.SelectedTopics);
    console.log(this.UserAddedTopics);
  }


  delUserTopic(topic){
    console.log("i am topic in deleeeeeeeeeeeete" , topic);
    console.log("i am the selected topics in deleeeeeeete", this.SelectedTopics);
    this.SelectedTopics.forEach((element,index)=>{
      if(element== topic) this.SelectedTopics.splice(index,1);
   });
   this.UserAddedTopics.forEach((element,index)=>{
    if(element== topic) this.UserAddedTopics.splice(index,1);

    console.log(this.SelectedTopics);
    console.log(this.UserAddedTopics);
 });
  }

  submit(){

   // console.log("IN SUBMIIIIT" , this.SelectedTopics);

    this.HttpService.SubmitSpecs(this.uuid,this.SelectedTopics,this.QForm.getRawValue())
    .subscribe(data => {

      console.log('i am the data ',data)

      this.router.navigate(['/exam'])
    }, error => {
      //alert("Error match couldn't be done please try another input")

    }
    )
  }


}
