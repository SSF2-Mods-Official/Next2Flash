package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class SSpecialAir_35 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;
        public var landlag:Boolean;

        public function SSpecialAir_35()
        {
            super();
            addFrameScript(0, this.frame1, 8, this.frame9, 20, this.frame21, 21, this.frame22, 28, this.frame29);
        }

        public function toGround(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
            this.self.setGlobalVariable("SimonSSpecFrame", currentFrame);
            this.self.forceAttack("b_forward", null, true);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            this.landlag = false;
            if (SSF2API.isReady() && this.self)
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
            };
        }

        internal function frame9():*
        {
            this.self.fireProjectile("cross_boomerang", 20, -30);
            this.self.playAttackSound(1);
            this.self.playVoiceSound(1);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }

        internal function frame22():*
        {
            this.landlag = true;
        }

        internal function frame29():*
        {
            this.self.endAttack();
        }


    }
}

