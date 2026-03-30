package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class Revival_10 extends MovieClip
    {

        public var stance:MovieClip;
        public var self:ChibiExt;

        public function Revival_10()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        public function fireTelly():void
        {
            this.self.fireProjectile("telly_vision");
            this.self.setGlobalVariable("telly", this.self.getCurrentProjectile());
        }

        internal function frame1():*
        {
            var _local_1:* = __activation__;
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (SSF2API.isReady())
            {
                this.self.setGlobalVariable("canStartRise", true);
                this.self.setIntangibility(false);
            };
            if (this.self && !this.self.getGlobalVariable("telly_timer"))
            {
                this.self.createTimer(1, -1, this.fireTelly, {
                    "condition":function ():Boolean
                    {
                        return !(self.getGlobalVariable("telly"));
                    },
                    "persistent":true
                });
                this.self.setGlobalVariable("telly_timer", true);
                SSF2API.print(("Made telly_timer: " + this.self.getGlobalVariable("telly_timer")));
            };
        }


    }
}

