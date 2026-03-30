package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class DSpecialAir_37 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function DSpecialAir_37()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 16, this.frame17);
        }

        public function toGround(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
            this.self.setGlobalVariable("SimonDSpecFrame", currentFrame);
            this.self.forceAttack("b_down", null, true);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
            };
        }

        internal function frame8():*
        {
            this.self.fireProjectile("water", 0, -30);
            this.self.playAttackSound(1);
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }


    }
}

