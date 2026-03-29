package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class NAir_119 extends MovieClip
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

        public function NAir_119()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 7, this.frame8, 8, this.frame9, 18, this.frame19, 20, this.frame21, 21, this.frame22, 25, this.frame26);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setLandingLag(false);
            };
            if (SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame2():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame3():*
        {
            this.self.setLandingLag(true);
            this.self.addEffectToList(this.self.attachEffect("trail_cfalcon_nair", {
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

        internal function frame8():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":7,
                "direction":45,
                "power":40,
                "kbConstant":100,
                "hitStun":3,
                "selfHitStun":1,
                "weightKB":0,
                "hitLag":-1.1
            });
            this.self.updateAttackBoxStats(2, {
                "damage":7,
                "direction":45,
                "power":40,
                "kbConstant":100,
                "hitStun":3,
                "selfHitStun":1,
                "weightKB":0,
                "hitLag":-1.1
            });
            this.self.refreshAttackID();
        }

        internal function frame9():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(43),
                "y":-27,
                "parentLock":true
            });
        }

        internal function frame19():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }

        internal function frame22():*
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

        internal function frame26():*
        {
            this.self.endAttack();
        }


    }
}

