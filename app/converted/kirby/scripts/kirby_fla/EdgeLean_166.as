package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class EdgeLean_166 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var fatstand:*;
        public var idle_repeat:*;

        public function EdgeLean_166()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.fatstand = false;
            this.idle_repeat = 0;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("kirbyPeachUsed", false);
            };
        }


    }
}

