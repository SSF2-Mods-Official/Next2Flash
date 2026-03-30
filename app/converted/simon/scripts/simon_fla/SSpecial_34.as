package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class SSpecial_34 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;
        public var curFrame:int;

        public function SSpecial_34()
        {
            super();
            addFrameScript(0, this.frame1, 8, this.frame9, 20, this.frame21, 28, this.frame29);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (SSF2API.isReady() && this.self)
            {
                this.curFrame = this.self.getGlobalVariable("SimonSSpecFrame");
                this.self.setGlobalVariable("SimonSSpecFrame", 0);
                if (this.curFrame > 1)
                {
                    this.self.stancePlayFrame(this.curFrame);
                };
            };
        }

        internal function frame9():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.fireProjectile("cross_boomerang", 20, -30);
                this.self.playAttackSound(1);
                this.self.playVoiceSound(1);
                this.self.attachEffect("global_dust_light");
            };
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }

        internal function frame29():*
        {
            this.self.endAttack();
        }


    }
}

