package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Fall_76 extends MovieClip
    {

        public var hand:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var fatfall:*;

        public function Fall_76()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 5, this.frame6, 9, this.frame10);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.fatfall = false;
            if (SSF2API.isReady() && this.self)
            {
                this.self.stancePlayFrame("back");
            };
        }

        internal function frame5():*
        {
            this.self.stancePlayFrame("back");
        }

        internal function frame6():*
        {
            this.fatfall = true;
        }

        internal function frame10():*
        {
            this.self.stancePlayFrame("fatfall");
        }


    }
}

