package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class UAir_120 extends MovieClip
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

        public function UAir_120()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 5, this.frame6, 6, this.frame7, 14, this.frame15, 17, this.frame18, 18, this.frame19, 22, this.frame23);
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

        internal function frame3():*
        {
            this.self.setLandingLag(true);
            this.self.addEffectToList(this.self.attachEffect("trail_cfalcon_uair", {
                "y":5,
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame5():*
        {
            this.self.playAttackSound(1);
            this.self.updateAttackBoxStats(1, {
                "damage":10,
                "power":15,
                "kbConstant":90
            });
            this.self.updateAttackBoxStats(2, {
                "damage":10,
                "power":15,
                "kbConstant":90
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
        }

        internal function frame6():*
        {
            this.self.updateAttackBoxStats(2, {
                "direction":30,
                "damage":8,
                "power":8,
                "kbConstant":80
            });
        }

        internal function frame7():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":8,
                "direction":0,
                "power":6,
                "kbConstant":70,
                "selfHitStun":1,
                "hitStun":1,
                "hitLag":-1
            });
            this.self.updateAttackBoxStats(2, {
                "damage":6,
                "direction":0,
                "power":6,
                "kbConstant":70,
                "selfHitStun":1,
                "hitStun":1,
                "hitLag":-1
            });
        }

        internal function frame15():*
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

        internal function frame23():*
        {
            this.self.endAttack();
        }


    }
}

