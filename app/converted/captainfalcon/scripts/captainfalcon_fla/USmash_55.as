package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class USmash_55 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;
        public var xframe:String;
        public var chargeTime:*;
        public var damageCharged:Number;

        public function USmash_55()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 45, this.frame46, 46, this.frame47, 48, this.frame49, 49, this.frame50, 50, this.frame51, 54, this.frame55, 55, this.frame56, 59, this.frame60, 60, this.frame61, 65, this.frame66);
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            this.xframe = null;
        }

        internal function frame6():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame46():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame47():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
            this.chargeTime = (this.self.getExecTime() - 1);
            this.damageCharged = (((2 * this.chargeTime) / 40) + 4);
            this.self.updateAttackBoxStats(1, {"damage":this.damageCharged});
            this.self.updateAttackBoxStats(2, {"damage":this.damageCharged});
        }

        internal function frame49():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame50():*
        {
            this.self.playVoiceSound(1);
            this.self.playSound("cfalcon_smashstart");
        }

        internal function frame51():*
        {
            this.self.playAttackSound(1);
            this.self.addEffectToList(this.self.attachEffect("trail_cfalcon_usmash", {
                "y":20,
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame55():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":13,
                "power":30,
                "kbConstant":128,
                "effectSound":"brawl_kick_l",
                "weightKB":0,
                "direction":70
            });
            this.self.updateAttackBoxStats(2, {
                "damage":12,
                "power":30,
                "kbConstant":110,
                "effectSound":"brawl_kick_l",
                "weightKB":0,
                "direction":70
            });
            this.self.playSound("cfalcon_smashstart");
            this.self.refreshAttackID();
        }

        internal function frame56():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame60():*
        {
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame61():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            };
        }

        internal function frame66():*
        {
            this.self.endAttack();
        }


    }
}

