package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class fsmashEffect_133 extends MovieClip
    {

        public var self:*;
        public var character:*;

        public function fsmashEffect_133()
        {
            super();
            addFrameScript(0, this.frame1, 15, this.frame16);
        }

        public function lock():void
        {
            if (this.character.getMC().currentFrameLabel == "a_forwardsmash")
            {
                this.self.setX(this.character.getX());
                this.self.setY(this.character.getY());
            }
            else
            {
                this.self.destroy();
            };
        }

        public function remove(_arg_1:*):void
        {
            if (!this.self.isDisposed())
            {
                this.self.destroyTimer(this.lock);
                this.character.removeEventListener(SSF2Event.CHAR_HURT, this.remove);
                this.self.destroy();
            };
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
                this.character.addEventListener(SSF2Event.CHAR_HURT, this.remove);
                this.self.createTimer(1, -1, this.lock);
            };
        }

        internal function frame16():*
        {
            this.self.destroyTimer(this.lock);
            this.self.destroy();
        }


    }
}

