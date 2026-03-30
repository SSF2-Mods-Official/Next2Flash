package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class DAir_61 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var playsound:Number;
        public var audio:Number;

        public function DAir_61()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 5, this.frame6, 6, this.frame7, 22, this.frame23, 27, this.frame28, 29, this.frame30, 30, this.frame31, 39, this.frame40, 40, this.frame41, 55, this.frame56);
        }

        public function toSuccess(_arg_1:*=null):void
        {
            this.self.stancePlayFrame("success");
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (this.self && SSF2API.isReady())
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.setLandingLag(false);
            };
        }

        internal function frame2():*
        {
            this.self.setYSpeed(0);
            this.self.setXSpeed(0);
            this.self.updateAttackStats({"air_ease":0});
        }

        internal function frame3():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame6():*
        {
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
            this.self.playAttackSound(1);
        }

        internal function frame7():*
        {
            this.self.updateAttackStats({
                "air_ease":-1,
                "allowControl":true
            });
            this.self.setYSpeed(10.7);
            this.self.setXSpeed(0);
        }

        internal function frame23():*
        {
            this.self.updateAttackStats({"refreshRate":9999});
            this.self.updateAttackBoxStats(1, {
                "damage":5,
                "direction":270,
                "power":60,
                "kbConstant":70
            });
            this.self.updateAttackBoxStats(2, {
                "damage":5,
                "direction":270,
                "power":60,
                "kbConstant":70
            });
            this.self.refreshAttackID();
        }

        internal function frame28():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame30():*
        {
            this.self.endAttack();
        }

        internal function frame31():*
        {
            this.self.attachEffect("effect_bdee_land", {"y":-20});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("bandanadee_dashstop");
            };
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.toSuccess);
            this.self.updateAttackBoxStats(1, {
                "damage":5,
                "direction":75,
                "power":40,
                "kbConstant":75
            });
            this.self.refreshAttackID();
        }

        internal function frame40():*
        {
            this.self.endAttack();
        }

        internal function frame41():*
        {
            this.self.setYSpeed(-11);
            this.self.setXSpeed(-6.5, false);
            this.self.setLandingLag(false);
        }

        internal function frame56():*
        {
            this.self.endAttack();
        }


    }
}

