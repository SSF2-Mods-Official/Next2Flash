package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class DSpecial_36 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;
        public var curFrame:int;

        public function DSpecial_36()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 17, this.frame18);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (SSF2API.isReady() && this.self)
            {
                this.curFrame = this.self.getGlobalVariable("SimonDSpecFrame");
                this.self.setGlobalVariable("SimonDSpecFrame", 0);
                if (this.curFrame > 1)
                {
                    this.self.stancePlayFrame(this.curFrame);
                };
            };
        }

        internal function frame8():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.fireProjectile("water", 20, -30);
                this.self.playAttackSound(1);
                this.self.attachEffect("global_dust_heavy", {
                    "scaleX":0.7,
                    "scaleY":0.55
                });
            };
        }

        internal function frame18():*
        {
            this.self.endAttack();
        }


    }
}

