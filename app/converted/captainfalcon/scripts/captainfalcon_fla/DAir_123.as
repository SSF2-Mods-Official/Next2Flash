package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class DAir_123 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;
        public var playsound:Number;
        public var audio:Number;

        public function DAir_123()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 8, this.frame9, 11, this.frame12, 19, this.frame20, 21, this.frame22, 22, this.frame23, 29, this.frame30);
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setLandingLag(false);
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame4():*
        {
            this.self.attachEffect("global_spark", {
                "x":this.flipX(5),
                "y":-15
            });
            this.self.setLandingLag(true);
        }

        internal function frame9():*
        {
            this.self.playAttackSound(1);
            this.self.playSound("brawl_swing_l");
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(8),
                "y":15,
                "parentLock":true
            });
            if ((this.playsound > 0.2) && (this.playsound <= 0.4) && (this.audio != 1))
            {
                this.self.playVoiceSound(1);
                this.self.setGlobalVariable("audio", 1);
            };
            if ((this.playsound > 0.4) && (this.playsound <= 0.6) && (this.audio != 2))
            {
                this.self.playVoiceSound(2);
                this.self.setGlobalVariable("audio", 2);
            };
            if ((this.playsound > 0.6) && (this.playsound <= 0.8) && (this.audio != 3))
            {
                this.self.playVoiceSound(3);
                this.self.setGlobalVariable("audio", 3);
            };
            if ((this.playsound > 0.8) && (this.playsound <= 1) && (this.audio != 4))
            {
                this.self.playVoiceSound(4);
                this.self.setGlobalVariable("audio", 4);
            };
            this.self.addEffectToList(this.self.attachEffect("trail_cfalcon_dair", {
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame12():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame20():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame22():*
        {
            this.self.endAttack();
        }

        internal function frame23():*
        {
            this.self.removeAllEffects();
            SSF2API.getCamera().shake(3);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_l");
            }
            else
            {
                this.self.playSound("falcon_dspecLand");
            };
        }

        internal function frame30():*
        {
            this.self.endAttack();
        }


    }
}

