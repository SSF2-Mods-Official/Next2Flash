package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class DashAttack_49 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;
        public var playsound:Number;
        public var audio:Number;

        public function DashAttack_49()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 3, this.frame4, 4, this.frame5, 15, this.frame16, 19, this.frame20);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as CaptainExt);
            };
        }

        internal function frame2():*
        {
            this.playsound = SSF2API.random();
            this.audio = this.self.getGlobalVariable("audio");
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame4():*
        {
            if ((root != null) && (parent != null))
            {
                this.self.playAttackSound(1);
            };
            if ((root != null) && (parent != null))
            {
                this.self.setXSpeed(17, false);
            };
            this.self.attachEffect("wind_wave", {
                "x":this.self.flipX(35),
                "y":-35,
                "scaleX":0.8,
                "scaleY":0.8,
                "parentLock":true
            });
            if ((this.playsound > 0.2) && (this.playsound <= 0.4) && (this.audio != 1))
            {
                if ((root != null) && (parent != null))
                {
                    this.self.playVoiceSound(1);
                };
                if ((root != null) && (parent != null))
                {
                    this.self.setGlobalVariable("audio", 1);
                };
            };
            if ((this.playsound > 0.4) && (this.playsound <= 0.6) && (this.audio != 2))
            {
                if ((root != null) && (parent != null))
                {
                    this.self.playVoiceSound(2);
                };
                if ((root != null) && (parent != null))
                {
                    this.self.setGlobalVariable("audio", 2);
                };
            };
            if ((this.playsound > 0.6) && (this.playsound <= 0.8) && (this.audio != 3))
            {
                if ((root != null) && (parent != null))
                {
                    this.self.playVoiceSound(3);
                };
                if ((root != null) && (parent != null))
                {
                    this.self.setGlobalVariable("audio", 3);
                };
            };
            if ((this.playsound > 0.8) && (this.playsound <= 1) && (this.audio != 4))
            {
                if ((root != null) && (parent != null))
                {
                    this.self.playVoiceSound(4);
                };
                if ((root != null) && (parent != null))
                {
                    this.self.setGlobalVariable("audio", 4);
                };
            };
        }

        internal function frame5():*
        {
            this.self.updateAttackBoxStats(1, {"damage":8});
        }

        internal function frame16():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            };
        }

        internal function frame20():*
        {
            this.self.endAttack();
        }


    }
}

