package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class ForwardThrow_59 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var touchBox:MovieClip;
        public var self:ChibiExt;

        public function ForwardThrow_59()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 13, this.frame14);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
        }

        internal function frame6():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame14():*
        {
            this.self.endAttack();
        }


    }
}

