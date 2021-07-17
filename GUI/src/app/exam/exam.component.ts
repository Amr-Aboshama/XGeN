import { exam } from './../exam';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import jspdf from 'jspdf';
import html2canvas from 'html2canvas';


@Component({
  selector: 'app-exam',
  templateUrl: './exam.component.html',
  styleUrls: ['./exam.component.css']
})
export class ExamComponent implements OnInit {

  exam : exam;
  wh_questions: string[];
  mcq_questions: string[];
  bool_questions: string[];
  tf_questions: string[];

  constructor() {
    this.exam = JSON.parse(localStorage.getItem('exam'));
    console.log(" I AM THE EXAM IN THE EXAM PAGE", this.exam);
    this.wh_questions=this.exam.wh_questions;
    this.mcq_questions =  this.exam.mcq_questions;
    this.bool_questions = this.exam.bool_questions;
    this.tf_questions = this.exam.tf_questions;
   // console.log("I AM the MCQ questions", this.mcq_questions);
   }

  ngOnInit(): void {
  }


  exportAsPDF(divId,name)
    {
      //var pdf = new jspdf('l', 'pt', 'a4' );
      var pdf = new jspdf('p', 'pt', [1050, 1300] );
      pdf.setFontSize(2);
      var doc=document.getElementById(divId);
      doc.setAttribute("padding","100px");

      pdf.html(doc, {
         callback: function (pdf) {
           pdf.save(name);
         }
      });
      ;
    }






}
