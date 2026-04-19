package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1555")]
   public dynamic class TechRoll_137 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function TechRoll_137()
      {
         super();
         addFrameScript(0,this.frame1,10,this.frame11,20,this.frame21);
      }
      
      internal function frame1() : *
      {
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
         if(SSF2API.isReady() && Boolean(this.self))
         {
            this.self.setIntangibility(true);
            this.self.setGlobalVariable("canStartRise",true);
            if(!this.self.getMetalStatus())
            {
               this.self.playSound("menumove",true);
            }
         }
      }
      
      internal function frame11() : *
      {
         this.self.setIntangibility(false);
      }
      
      internal function frame21() : *
      {
         this.self.endAttack();
      }
   }
}

