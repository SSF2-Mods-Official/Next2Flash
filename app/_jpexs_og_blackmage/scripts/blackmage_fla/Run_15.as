package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1318")]
   public dynamic class Run_15 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function Run_15()
      {
         super();
         addFrameScript(0,this.frame1,3,this.frame4,6,this.frame7,7,this.frame8,11,this.frame12,15,this.frame16,19,this.frame20);
      }
      
      internal function frame1() : *
      {
         if(SSF2API.isReady())
         {
            this.self = SSF2API.getCharacter(this) as BlackMageExt;
         }
         if(Boolean(parent) && SSF2API.isReady())
         {
            this.self.playSound("run_start");
         }
      }
      
      internal function frame4() : *
      {
         if(this.self.getMetalStatus())
         {
            this.self.playSound("metal_step_s2");
         }
         else
         {
            this.self.playSound("bm_footstep");
         }
      }
      
      internal function frame7() : *
      {
         this.self.stancePlayFrame("run");
      }
      
      internal function frame8() : *
      {
         if(this.self.getMetalStatus())
         {
            this.self.playSound("metal_step_s1");
         }
         else
         {
            this.self.playSound("bm_footstep");
         }
      }
      
      internal function frame12() : *
      {
         if(this.self.getMetalStatus())
         {
            this.self.playSound("metal_step_s2");
         }
         else
         {
            this.self.playSound("bm_footstep");
         }
      }
      
      internal function frame16() : *
      {
         this.self.stancePlayFrame("run");
      }
      
      internal function frame20() : *
      {
         if(this.self.getMetalStatus())
         {
            this.self.playSound("metal_land_s");
         }
         else
         {
            this.self.playSound("blackmage_landLight");
         }
      }
   }
}

