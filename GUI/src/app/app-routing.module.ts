import { ExamComponent } from './exam/exam.component';
import { TopicsComponent } from './topics/topics.component';
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';


const routes: Routes = [

  {path: 'exam' , component: ExamComponent},
  {path: 'topics' , component: TopicsComponent },
  {path: 'home' , component: HomeComponent },
  { path: "**", redirectTo: "home", pathMatch: "full" }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
