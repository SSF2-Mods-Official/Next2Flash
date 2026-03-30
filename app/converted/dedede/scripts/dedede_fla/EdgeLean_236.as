package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class EdgeLean_236 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var hitBox6:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public var rand:int;

        public function EdgeLean_236()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 39, this.frame40);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
        }

        internal function frame3():*
        {
            this.rand = (10 * SSF2API.random());
            if ((this.rand >= 8) && !(this.self.getMetalStatus()))
            {
                this.self.playSound("ssf2_snd_vfx_dedede_edgeLean", true);
            };
        }

        internal function frame40():*
        {
            gotoAndStop("loop");
        }


    }
}

