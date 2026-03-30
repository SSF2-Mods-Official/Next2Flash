package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class DThrow_121 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var touchBox:MovieClip;
        public var self:KirbyExt;
        public var xframe:String;
        public var playsound:Number;
        public var audio:Number;

        public function DThrow_121()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 4, this.frame5, 23, this.frame24, 30, this.frame31, 38, this.frame39);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.xframe = null;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.forceGrabbedHurtFrame("faint");
            };
        }

        internal function frame2():*
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

        internal function frame5():*
        {
            this.self.forceGrabbedHurtFrame("downed");
        }

        internal function frame24():*
        {
            this.self.updateAttackBoxStats(2, {
                "damage":2,
                "bypassNonGrabbed":false,
                "hasEffect":true,
                "hitStun":5,
                "selfHitStun":4,
                "sdiDistance":1.2,
                "direction":78,
                "kbConstant":180,
                "effect_id":"effect_heavyHit",
                "effectSound":"brawl_kick_l"
            });
            this.self.refreshAttackID();
        }

        internal function frame31():*
        {
            SSF2API.getCamera().shake(10);
            this.self.attachEffect("global_dust_cloud");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playAttackSound(2);
            };
        }

        internal function frame39():*
        {
            this.self.endAttack();
        }


    }
}

