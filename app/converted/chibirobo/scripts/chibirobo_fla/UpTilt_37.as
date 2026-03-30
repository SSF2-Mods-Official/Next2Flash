package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class UpTilt_37 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var xframe:*;

        public function UpTilt_37()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 7, this.frame8, 15, this.frame16);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            this.xframe = null;
            if (SSF2API.isReady() && this.self)
            {
            };
        }

        internal function frame5():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-7)});
        }

        internal function frame8():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            };
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }


    }
}

