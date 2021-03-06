#! /usr/bin/env python

from ROOT import TStyle, TF1, TFile, TCanvas, gDirectory, TTree, TH1F, TH2F, THStack, TLegend, gROOT 
import ROOT

from style import *

from collections import OrderedDict
datasamples=OrderedDict()
bkgsamples=OrderedDict()
sigsamples=OrderedDict()

def SetData(file, name, lumi):
  tmp = {}
  f = TFile(file)
  fnames = f.GetName().split('.')
  fname = fnames[0]

  tmp["file"] = f
  tmp["hname"] = [x.GetName() for x in f.GetListOfKeys()]
  tmp["hname"].remove("EventInfo")
  tmp["lumi"] = lumi 
  tmp["name"] = name
  datasamples[fname] = tmp
 
def AddBkg(file, name, color, xsection):
  tmp = {}
  f = TFile(file)
  fnames = f.GetName().split('.')
  fname = fnames[0]
 
  tmp["file"] = f
  tmp["hname"] = [x.GetName() for x in f.GetListOfKeys()]
  tmp["hname"].remove("EventInfo")

  #debug
  #N_h = len(tmp["hname"])
  tmp_h = f.Get(tmp["hname"][0])
  tmp_n = tmp_h.Integral()
  print fname, " : ", name, " : ", tmp["hname"][0], " : " , tmp_n

  h = f.Get("EventInfo")
  nevt = h.GetBinContent(2)
  tmp["total"] = nevt 
  tmp["col"] = color
  tmp["xsection"] = xsection
  tmp["name"] = name
  bkgsamples[fname] = tmp

####Users should provide these information 
SetData("hist_DataSingleMu.root","data", 35867) # for now, combination of muon and electron
SetData("hist_DataSingleEG.root","data", 35867) # for now, combination of muon and electron
AddBkg("hist_ttbb.root","ttbb",ROOT.kRed+4, 365.4)
AddBkg("hist_ttbj.root","ttbj",ROOT.kRed+3, 365.4)
AddBkg("hist_ttcc.root","ttcc",ROOT.kRed+2, 365.4)
AddBkg("hist_ttLF.root","ttLF",ROOT.kRed, 365.4)
AddBkg("hist_tt.root","ttLF",ROOT.kRed, 356.4)
AddBkg("hist_ttBkg.root","ttLF",ROOT.kRed, 831.8)
AddBkg("hist_wjets.root","WJets",ROOT.kYellow,61524)
AddBkg("hist_zjets.root","ZJets",ROOT.kBlue, 6025.2)
AddBkg("hist_zjets10to50.root","ZJets",ROOT.kBlue, 18610.0)
AddBkg("hist_tchannel.root","Single t",6, 44.33)
AddBkg("hist_tbarchannel.root","Single t",6, 26.38)
AddBkg("hist_tWchannel.root","Single t",6, 35.6)
AddBkg("hist_tbarWchannel.root","Single t",6, 35.6)
AddBkg("hist_ww.root","DiBoson",ROOT.kCyan, 118.7)
AddBkg("hist_wz.root","DiBoson",ROOT.kCyan, 47.13)
AddBkg("hist_zz.root","DiBoson",ROOT.kCyan, 16.523)
#### 

N_hist = len(datasamples[datasamples.keys()[0]]["hname"])
N_bkgsamples = len(bkgsamples)

for i in range(0, N_hist):
  if "Ch0" in datasamples[datasamples.keys()[0]]["hname"][i]:
    mode = 0
  else:
    mode = 1 

  hs = THStack()
  #l = TLegend(0.30, 0.99 - 0.8 * N_bkgsamples / 20., 0.89, 0.85)
  l = TLegend(0.15,0.71,0.89,0.87)
  l.SetNColumns(4);
  l.SetTextSize(0.04);
  l.SetLineColor(0);
  l.SetFillColor(0);

  ntotalbkg = 0
  k = 0
  for fname in bkgsamples.keys():
    h_tmp = bkgsamples[fname]["file"].Get(bkgsamples[fname]["hname"][i])
    h_tmp.SetFillColor(bkgsamples[fname]["col"])
    ## check if the sample is the same as previous process. 
    if k < N_bkgsamples-1 :
      post_name = bkgsamples.keys()[k+1]
      if bkgsamples[fname]["name"] is bkgsamples[post_name]["name"]:
        bkgsamples[fname]["file"].Get(bkgsamples[fname]["hname"][i]).SetLineColor(bkgsamples[fname]["col"]) 
      else:
        l.AddEntry(h_tmp, bkgsamples[fname]["name"]  ,"F") 
    else: 
      l.AddEntry(h_tmp, bkgsamples[fname]["name"]  ,"F")
    ## normalization
    scale = datasamples[datasamples.keys()[mode]]["lumi"]/(bkgsamples[fname]["total"]/bkgsamples[fname]["xsection"])
    h_tmp.Scale(scale)
    numevt = h_tmp.Integral()
    rawevt = h_tmp.GetEntries()
    ntotalbkg = ntotalbkg + numevt
    print fname, " : ", bkgsamples[fname]["name"], " = ", "{0:.6g}".format(numevt), " raw : ", "{0:.1g}".format(rawevt), " scale : " ,"{0:.1g}".format(scale)  
    hs.Add( h_tmp )
    k = k+1 

  c = TCanvas("c_"+"{}".format(i),"c",1)
  h_data = datasamples[datasamples.keys()[mode]]["file"].Get(datasamples[datasamples.keys()[mode]]["hname"][i])
  h_data.SetMarkerStyle(20)
  h_data.SetMarkerSize(0.3)
  max_data = h_data.GetMaximum()
  max_hs = hs.GetMaximum()
  if max_hs > max_data :
    h_data.SetMaximum(max_hs+max_hs*0.5)
  else:
    h_data.SetMaximum(max_data+max_data*0.5)
  h_data.Draw("p")
  h_data.SetTitle("")
  h_data.GetYaxis().SetTitle("Entries")
  hs.Draw("histsame")
  h_data.Draw("psame")

  l.AddEntry(h_data,"Data","P")
  l.Draw()
  label = TPaveText()
  label.SetX1NDC(gStyle.GetPadLeftMargin())
  label.SetY1NDC(1.0-gStyle.GetPadTopMargin())
  label.SetX2NDC(1.0-gStyle.GetPadRightMargin())
  label.SetY2NDC(1.0)
  label.SetTextFont(42)
  label.AddText("CMS, 35.9 fb^{-1} at #sqrt{s} = 13 TeV")
  label.SetFillStyle(0)
  label.SetBorderSize(0)
  label.SetTextSize(0.04)
  label.SetTextAlign(32)
  label.Draw("same")

  ndata = h_data.Integral()
  print "ntotal = " , "{0:.6g}".format(ntotalbkg)
  print "ndata = " , "{0:.0f}".format(ndata)

  c.Print("c_"+datasamples[datasamples.keys()[mode]]["hname"][i]+".pdf")
  filename = "result.pdf"
  if i == 0 and N_hist > 1:
    c.Print( (filename+"(") )
  elif i > 0 and i == N_hist-1:
    c.Print( (filename+")") ) 
  else:
    c.Print(filename)

