package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fspecEffect_165 extends MovieClip
    {

        public var self:*;
        public var timer:*;
        public var character:*;

        public function fspecEffect_165()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6);
        }

        public function lock():void
        {
            this.self.setX(this.character.getGlobalVariable(("dashX" + this.timer)));
            this.self.setY((this.character.getGlobalVariable(("dashY" + this.timer)) + 5));
            this.timer++;
            if (this.timer == (this.character.getGlobalVariable("dashLim") - 1))
            {
                this.self.destroy();
            };
        }

        public function remove(_arg_1:*):void
        {
            this.character.removeEventListener(SSF2Event.CHAR_HURT, this.remove);
            this.self.destroy();
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.timer = 0;
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
                this.character.addEventListener(SSF2Event.CHAR_HURT, this.remove);
                this.self.createTimer(1, -1, this.lock);
            };
        }

        internal function frame6():*
        {
            this.gotoAndStop("loop");
        }


    }
}

