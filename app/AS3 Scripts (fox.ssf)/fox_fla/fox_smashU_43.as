// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.fox_smashU_43

package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_smashU_43 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;
        public var xframe:String;

        public function fox_smashU_43()
        {
            addFrameScript(0, this.frame1, 2, this.frame3, 42, this.frame43, 43, this.frame44, 46, this.frame47, 47, this.frame48, 48, this.frame49, 52, this.frame53, 63, this.frame64);
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(8),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
        }

        internal function frame3():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame43():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame44():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
            this.self.playVoiceSound(1);
            this.self.playAttackSound(2);
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame47():*
        {
            this.self.playAttackSound(1);
            this.self.playAttackSound(3);
        }

        internal function frame48():*
        {
        }

        internal function frame49():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":6,
                "camShake":-1,
                "power":50,
                "direction":50,
                "kbConstant":70,
                "effectSound":"brawl_kick_m",
                "effect_id":"effect_lightHit"
            });
            this.self.updateAttackBoxStats(2, {
                "damage":6,
                "camShake":-1,
                "power":50,
                "direction":50,
                "kbConstant":70,
                "effectSound":"brawl_kick_m",
                "effect_id":"effect_lightHit"
            });
        }

        internal function frame53():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("fox_landLight");
            };
        }

        internal function frame64():*
        {
            this.self.endAttack();
        }


    }
}//package fox_fla

