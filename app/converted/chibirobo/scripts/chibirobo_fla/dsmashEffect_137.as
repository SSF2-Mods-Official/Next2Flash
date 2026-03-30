package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class dsmashEffect_137 extends MovieClip
    {

        public var self:*;
        public var character:*;

        public function dsmashEffect_137()
        {
            super();
            addFrameScript(0, this.frame1, 14, this.frame15);
        }

        public function lock():void
        {
            if (this.character.getMC().currentFrameLabel == "a_down")
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
                this.self.createTimer(1, -1, this.lock);
            };
        }

        internal function frame15():*
        {
            this.self.destroyTimer(this.lock);
            this.self.destroy();
        }


    }
}

