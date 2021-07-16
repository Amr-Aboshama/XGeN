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


  exportAsPDF(divId)
    {
      //var pdf = new jspdf('l', 'pt', 'a4' );
      var pdf = new jspdf('p', 'pt', [900, 1300] );



      pdf.setFontSize(2);
      var doc=document.getElementById(divId);
      doc.setAttribute("padding","100px");

      pdf.html(doc, {
         callback: function (pdf) {
           pdf.save('exam.pdf');
         }
      });

//       https://stackoverflow.com/questions/18191893/generate-pdf-from-html-in-div-using-javascript
//var doc = new jspdf();
// var elementHandler = {
//   '#ignorePDF': function (element, renderer) {
//     return true;
//   }
// };
// var source = "<div><h1>hello</h1></div>";
// doc.html(source,{'ckmdkc'}, 15);
//     doc.save('Filename.pdf');

// doc.output("dataurlnewwindow");
      //console.log('1 ###########' , divId);
      //  let data = document.getElementById(divId);
//
      //  console.log('2 ###########', data);
//
      //  let canvas = html2canvas(data)
      //  //const contentDataURL = canvas.toDataURL('image/png')
      //  console.log('3 ###########', canvas)
      //  let pdf = new jspdf('l', 'cm', 'a4'); //Generates PDF in landscape mode
      //  console.log('4 ###########');
      //  // let pdf = new jspdf('p', 'cm', 'a4'); Generates PDF in portrait mode
      //  console.log('5 ###########');
      //  //pdf.addImage(contentDataURL, 'PNG', 0, 0, 29.7, 21.0);
      //  pdf.html(data);
      //  pdf.save('Filename.pdf');
      //  console.log('6 ###########')
      ;
    }



}
