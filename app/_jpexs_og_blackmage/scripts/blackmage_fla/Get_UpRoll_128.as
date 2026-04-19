package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1545")]
   public dynamic class Get_UpRoll_128 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function Get_UpRoll_128()
      {
         super();
         addFrameScript(0,this.frame1,10,this.frame11,17,this.frame18);
      }
      
      internal function frame1() : *
      {
         if(SSF2API.isReady())
         {
            this.self = SSF2API.getCharacter(this) as BlackMageExt;
         }
         if(Boolean(parent) && SSF2API.isReady())
         {
            this.self.setIntangibility(true);
         }
      }
      
      internal function frame11() : *
      {
         this.self.setIntangibility(false);
      }
      
      internal function frame18() : *
      {
         this.self.endAttack();
      }
   }
}

