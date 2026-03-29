package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class BAir_122 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;
        public var playsound:Number;
        public var audio:Number;

        public function BAir_122()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 6, this.frame7, 15, this.frame16, 17, this.frame18, 18, this.frame19, 23, this.frame24);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            if (SSF2API.isReady())
            {
                this.self.setLandingLag(false);
            };
            if (SSF2API.isReady())
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame4():*
        {
            this.self.playAttackSound(1);
            this.self.setLandingLag(true);
        }

        internal function frame5():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(-28),
                "y":-25,
                "parentLock":true
            });
            this.self.addEffectToList(this.self.attachEffect("trail_cfalcon_bair", {
                "y":10,
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
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
        }

        internal function frame7():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":8,
                "direction":45,
                "power":20,
                "kbConstant":100,
                "hitStun":3,
                "selfHitStun":1
            });
            this.self.updateAttackBoxStats(2, {
                "damage":8,
                "direction":45,
                "power":20,
                "kbConstant":100
            });
        }

        internal function frame16():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame18():*
        {
            this.self.endAttack();
        }

        internal function frame19():*
        {
            this.self.removeAllEffects();
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("falcon_dspecLand");
            };
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}

