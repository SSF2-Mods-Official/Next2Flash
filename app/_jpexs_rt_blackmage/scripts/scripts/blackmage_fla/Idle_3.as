package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1280")]
   public dynamic class Idle_3 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public var used:Boolean;
      
      public var rand:int;
      
      public var repeats:int;
      
      public function Idle_3()
      {
         super();
         addFrameScript(0,this.frame1,11,this.frame12,35,this.frame36,65,this.frame66,69,this.frame70);
      }
      
      public function restoreSpecials() : *
      {
         this.self.setAttackEnabled(true,"b_forward");
         this.self.setAttackEnabled(true,"b_forward_air");
      }
      
      public function uncrouch(param1:* = null) : *
      {
         if(param1.data.fromState == 12 && this.self.getGlobalVariable("crouchdown"))
         {
            this.self.setGlobalVariable("crouchdown",false);
            this.self.stancePlayFrame("uncrouch");
         }
         else
         {
            this.self.setGlobalVariable("crouchdown",false);
         }
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:BlackMageExt = null;
         var _loc5_:Boolean = false;
         var _loc6_:int = 0;
         var _loc7_:int = 0;
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
         this.used = false;
         this.rand = 0;
         if(!this.repeats)
         {
            this.repeats = 0;
         }
         if(parent && SSF2API.isReady() && Boolean(this.self))
         {
            this.rand = 100 * SSF2API.random();
            if(this.rand >= 95)
            {
               this.gotoAndStop("bored");
            }
            else if(this.rand >= 85)
            {
               this.gotoAndStop("blink");
            }
         }
         if(SSF2API.isReady() && Boolean(this.self))
         {
            this.restoreSpecials();
         }
         if(this.self && SSF2API.isReady() && !this.self.hasEventListener(SSF2Event.STATE_CHANGE,this.uncrouch))
         {
            this.self.addEventListener(SSF2Event.STATE_CHANGE,this.uncrouch);
         }
      }
      
      internal function frame12() : *
      {
         ++this.repeats;
         this.gotoAndStop("loop");
      }
      
      internal function frame36() : *
      {
         ++this.repeats;
         this.gotoAndStop("loop");
      }
      
      internal function frame66() : *
      {
         this.gotoAndStop("loop");
      }
      
      internal function frame70() : *
      {
         gotoAndStop("loop");
      }
   }
}

