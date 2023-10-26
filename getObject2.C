#include <string>
#include <iostream>
#include <time.h>
#include <algorithm>
#include "QualityControl/DatabaseFactory.h"
#include "QualityControl/CcdbDatabase.h"
#include "QualityControl/MonitorObject.h"
#include "CCDB/CcdbObjectInfo.h"
#include "CCDB/CcdbApi.h"
#include <TBufferJSON.h>
#include <TH2.h>
#include <THnSparse.h>
#include <TFile.h>
#include <TTree.h>
#include <TSystem.h>


using namespace std;
using namespace o2::quality_control::repository;
using namespace o2::quality_control::core;

void getObject2(TString outfile="objectreport.txt"){
  /*
 string ccdburl = "http://ali-qcdb-gpn.cern.ch:8083"

 o2:ccdb:BasicCCDBManager& mgr = o2::ccdb::BasicCCDBManager::instance();


  */

 ofstream report;
 report.open(outfile);

 string ccdbport = "http://ali-qcdb-gpn.cern.ch:8083";

 std::unique_ptr<DatabaseInterface> mydb = DatabaseFactory::create("CCDB");

 auto* ccdb = dynamic_cast<CcdbDatabase*>(mydb.get());

 ccdb->connect(ccdbport.c_str(),"","","");

 string qcpath = "ITS/MO/ITSQualityTask";

 o2::ccdb::CcdbApi ccdbapi;
 ccdbapi.init(ccdbport.c_str());

 string object = ccdbapi.list("qc/"+qcpath+"/QualitySummary",false,"text/plain");

 stringstream ss(object);

 string word;
 vector<string> Val{};
 vector<string> Run{};
 vector<string> Created{};
 int found_n = 0;
 bool found_true = false;
 while(ss>>word){
   if (word=="Validity:") {ss>>word; Val.push_back(word); found_n++;}
   if (word=="RunNumber") {ss>>word; ss>>word; Run.push_back(word); }
   if (word=="Created:") {ss>>word; Created.push_back(word);}
   if (found_n > 1) break;
 }

 if (!found_n) {report<<"FOUND ANYTHING"; exit(0);}

 
 report<<"Starting object validity = "<<Val[0]<<endl;
 report<<"Object creation time = "<<Created[0]<<endl;
 report<<"RunNumber: "<<Run[0]<<endl;

 //auto monitor = ccdb->retrieveMO(qcpath, "ITSQuality", std::stol(Val[0]));
 auto monitor = ccdb->retrieveMO(qcpath, "QualitySummary", std::stol(Val[0]));

 ccdb->disconnect();
 
 TObject *obj = nullptr;
 obj = monitor->getObject();
 monitor->setIsOwner(false);
 string c = obj->ClassName();
 cout<<c<<endl;

 TCanvas *canv = (TCanvas*)obj;
 

 TList *L = (TList*)canv->GetListOfPrimitives();

 for (TObject *o : *L){
   cout<<o->GetName()<<" - "<<o->GetTitle()<<" - "<<o->ClassName()<<endl;
   if ((TString)(o->GetName()) == "TPave"){
     TPaveText* pav = (TPaveText*)o;
     gPad->SaveAs("qualitypave.png");
     TList *Lines = (TList*)(pav->GetListOfLines());
     for (TObject* line : *Lines){
       TText *txt = (TText*)line;
       report<<line->GetTitle()<<endl;
     }
   }
 }

 report.close();
 exit(0);

  
}

