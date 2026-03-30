package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class dairEffect_143 extends MovieClip
    {

        public var self:*;
        public var character:*;

        public function dairEffect_143()
        {
            super();
            addFrameScript(0, this.frame1, 13, this.frame14);
        }

        public function lock():void
        {
            if (this.character.getMC().currentFrameLabel == "a_air_down")
            {
                this.self.setX(this.character.getX());
                this.self.setY(this.character.getY());
            }
            else
            {
                this.character.removeEventListener(SSF2Event.GROUND_TOUCH, this.remove);
                this.self.destroy();
            };
        }

        public function remove(_arg_1:*):void
        {
            if (!this.self.isDisposed())
            {
                this.self.destroyTimer(this.lock);
                this.character.removeEventListener(SSF2Event.CHAR_HURT, this.remove);
                this.character.removeEventListener(SSF2Event.GROUND_TOUCH, this.remove);
                this.self.destroy();
            };
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
                this.character.addEventListener(SSF2Event.GROUND_TOUCH, this.remove);
                this.self.createTimer(1, -1, this.lock);
            };
        }

        internal function frame14():*
        {
            this.self.destroyTimer(this.lock);
            this.self.destroy();
        }


    }
}

