package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1547")]
   public dynamic class Taunts_130 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function Taunts_130()
      {
         super();
         addFrameScript(0,this.frame1,4,this.frame5,40,this.frame41,44,this.frame45,90,this.frame91,101,this.frame102,166,this.frame167);
      }
      
      internal function frame1() : *
      {
         if(SSF2API.isReady())
         {
            this.self = SSF2API.getCharacter(this) as BlackMageExt;
         }
      }
      
      internal function frame5() : *
      {
         if(!this.self.getMetalStatus())
         {
            this.self.playSound("bmtaunt3",true);
         }
      }
      
      internal function frame41() : *
      {
         if(this.self.getMetalStatus())
         {
            this.self.playSound("metal_land_s");
         }
      }
      
      internal function frame45() : *
      {
         this.self.endAttack();
      }
      
      internal function frame91() : *
      {
         this.self.endAttack();
      }
      
      internal function frame102() : *
      {
         if(!this.self.getMetalStatus())
         {
            this.self.playSound("bm_taunt3",true);
         }
         if(this.self.getMetalStatus())
         {
            this.self.playSound("bm_taunt3_metal");
         }
      }
      
      internal function frame167() : *
      {
         this.self.endAttack();
      }
   }
}

